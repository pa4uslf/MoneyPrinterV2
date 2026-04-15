import re
import sys
import time
import os
import json

from cache import *
from config import *
from status import *
from llm_provider import generate_text
from content_profile import (
    build_required_field_status,
    build_profile_context,
    has_service_strategy,
    load_case_brief,
    missing_required_strategy_fields,
    normalize_content_profile,
)
from typing import List, Optional
from datetime import datetime
from termcolor import colored
from selenium_firefox import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Twitter:
    """
    Class for the Bot, that grows a Twitter account.
    """

    _MAX_TWEET_LENGTH = 240
    _VALID_FIRST_MOVE_PREFIXES = (
        "check",
        "verify",
        "inspect",
        "list",
        "compare",
        "disable",
        "trace",
        "review",
    )
    _FIRST_MOVE_ACTION_KEYWORDS = (
        "route",
        "routes",
        "path",
        "paths",
        "auth",
        "proxy",
        "reverse proxy",
        "nginx",
        "config",
        "configuration",
        "port",
        "ports",
        "secret",
        "secrets",
        "env",
        "environment",
        "header",
        "headers",
        "admin",
        "public",
        "permission",
        "permissions",
    )
    _CTA_SHADOW_MARKERS = (
        "use our checklist",
        "use this checklist",
        "download",
        "learn more",
        "read the guide",
        "use this guide",
        "follow our framework",
        "follow this checklist",
        "use this template",
        "grab the template",
        "see the full list",
        "checklist",
        "template",
        "guide",
        "framework",
        "http://",
        "https://",
        "www.",
    )
    _EXPECTED_ATTRIBUTE_SHADOWS = (
        "clear first-pass deploy judgment",
        "no obvious exposure",
        "avoid deployment mistakes",
        "safer first release",
    )
    _VALID_BAD_INSTINCT_PREFIXES = (
        "the bad instinct is to ",
        "most builders assume ",
        "the risky default is to ",
        "the mistake is to ",
    )

    def _variant_instruction(self) -> str:
        """
        Returns a specialized instruction block for the selected service variant.

        Returns:
            instruction (str): Variant-specific prompt guidance
        """
        variant = self.content_profile.get("content_variant", "general")

        if variant == "deployment":
            return (
                "Focus on shipping a real project from repo to running environment. "
                "Prefer setup pitfalls, environment mismatches, hosting choices, or launch blockers."
            )
        if variant == "hardening":
            return (
                "Focus on security, auth, exposure, secret handling, backup gaps, or operational risk reduction."
            )
        if variant == "customization":
            return (
                "Focus on adapting an existing project to a workflow, client need, UI change, or integration requirement."
            )

        return (
            "Focus on practical implementation lessons that can become reusable content, downloadable resources, or low-touch monetizable assets."
        )

    def _asset_instruction(self) -> str:
        """
        Returns specialized guidance for the selected asset type.

        Returns:
            instruction (str): Asset-specific prompt guidance
        """
        asset_type = self.content_profile.get("asset_type", "")
        capture_type = self.content_profile.get("capture_type", "")
        monetization_type = self.content_profile.get("monetization_type", "")

        return (
            f"Primary asset type: {asset_type or 'general content asset'}. "
            f"Capture type: {capture_type or 'none'}. "
            f"Monetization type: {monetization_type or 'none'}. "
            "The post should nudge the reader toward a reusable business asset, owned destination, or owned relationship, not only a direct service sale."
        )

    def _demand_diagnostics_instruction(self) -> str:
        """
        Returns a compact instruction block for persona, scene, KANO, and stakeholder checks.

        Returns:
            instruction (str): Diagnostic guidance for prompt use
        """
        return (
            "Silently diagnose the topic before writing: identify the reader's real role, "
            "their strongest scene, what triggered the need now, what they fear will happen, "
            "which expected attribute must be delivered with certainty, what would only be a delighter, "
            "what could become a reverse attribute, and which stakeholder roles support or resist the next move."
        )

    def _tweet_mode_instruction(self) -> str:
        """
        Returns the smallest viable structure for an X post.

        Returns:
            instruction (str): Post-priority guidance
        """
        return (
            "Treat this as a two-sentence X post. Priority order is fixed: "
            "1) concrete scene, "
            "2) mistaken instinct or blind spot, "
            "3) first move, "
            "4) identity cue only if it fits naturally, "
            "5) CTA only if room remains. "
            "Do not try to fully explain why the usual approach fails if space gets tight."
        )

    def _field_hauling_block(self) -> str:
        """
        Returns explicit instructions that forbid copying profile-field wording.

        Returns:
            instruction (str): Anti-field-hauling guidance
        """
        return (
            "Do not copy profile fields verbatim into the post. "
            "Never directly repeat labels or raw phrases such as "
            "'desired identity', 'avoided identity', or 'expected attribute'. "
            "Translate them into natural language only if they fit the post."
        )

    def _field_hauling_examples(self) -> str:
        """
        Returns profile values that should not be copied verbatim.

        Returns:
            examples (str): Compact text block
        """
        blocked_values = []
        for key in ("desired_identity", "avoided_identity", "expected_attribute"):
            value = str(self.content_profile.get(key, "") or "").strip()
            if value:
                blocked_values.append(f"{key}={value}")

        return (
            "Field-hauling examples to avoid: " + " | ".join(blocked_values)
            if blocked_values
            else "Field-hauling examples to avoid: none provided."
        )

    def _cta_heuristic_present(self, text: str) -> bool:
        """
        Detects whether the post still contains a likely CTA.

        Args:
            text (str): Post text

        Returns:
            present (bool): True when CTA-like phrasing remains
        """
        lowered = str(text or "").lower()
        cta_markers = [
            "download",
            "subscribe",
            "learn more",
            "read more",
            "get the checklist",
            "grab the checklist",
            "checklist",
            "http://",
            "https://",
            "www.",
        ]
        return any(marker in lowered for marker in cta_markers)

    def _normalize_short_text(self, text: str) -> str:
        """
        Normalizes short text for hard checks.

        Args:
            text (str): Raw text

        Returns:
            normalized (str): Lowercased compact text
        """
        lowered = str(text or "").lower().strip()
        lowered = re.sub(r"[^a-z0-9\\s:/.-]", " ", lowered)
        return re.sub(r"\\s+", " ", lowered).strip()

    def _contains_cta_shadow(self, text: str) -> bool:
        """
        Detects CTA-shadow phrasing.

        Args:
            text (str): Candidate text

        Returns:
            present (bool): True when CTA-shadow phrasing exists
        """
        normalized = self._normalize_short_text(text)
        return any(marker in normalized for marker in self._CTA_SHADOW_MARKERS)

    def _contains_expected_attribute_leak(self, text: str) -> bool:
        """
        Detects exact or near-exact expected-attribute leakage.

        Args:
            text (str): Candidate text

        Returns:
            leaked (bool): True when result-style leakage exists
        """
        normalized = self._normalize_short_text(text)

        if any(marker in normalized for marker in self._EXPECTED_ATTRIBUTE_SHADOWS):
            return True

        expected_attribute = self._normalize_short_text(
            self.content_profile.get("expected_attribute", "")
        )
        if not expected_attribute:
            return False

        tokens = expected_attribute.split()
        if len(tokens) >= 3:
            ngrams = [" ".join(tokens[idx : idx + 3]) for idx in range(len(tokens) - 2)]
            if any(ngram in normalized for ngram in ngrams):
                return True

        return False

    def _is_valid_first_move(self, text: str) -> bool:
        """
        Validates that first_move is an internal deployment/config action.

        Args:
            text (str): Candidate first move

        Returns:
            valid (bool): True when valid
        """
        normalized = self._normalize_short_text(text)
        if not normalized:
            return False
        if self._contains_cta_shadow(normalized):
            return False
        if self._contains_expected_attribute_leak(normalized):
            return False
        if not normalized.startswith(self._VALID_FIRST_MOVE_PREFIXES):
            return False
        return any(keyword in normalized for keyword in self._FIRST_MOVE_ACTION_KEYWORDS)

    def _is_valid_bad_instinct(self, text: str) -> tuple[bool, str]:
        """
        Validates that bad_instinct is an explicit mistaken-instinct sentence, not a status or consequence.

        Args:
            text (str): Candidate bad instinct

        Returns:
            valid (bool): True when valid
            reason (str): Failure reason or ok
        """
        normalized = self._normalize_short_text(text)
        if not normalized:
            return False, "empty"

        if not normalized.startswith(self._VALID_BAD_INSTINCT_PREFIXES):
            return False, "must use an allowed mistaken-instinct sentence starter"

        status_markers = (
            "unclear",
            "confusing",
            "might accidentally",
            "i might",
            "there is a risk",
        )
        if any(marker in normalized for marker in status_markers):
            return False, "describes state or consequence instead of mistaken instinct"

        return True, "ok"

    def _compress_tweet_safely(self, scene: str, bad_instinct: str, first_move: str) -> tuple[str, str, str]:
        """
        Compresses sentence parts without breaking sentence integrity.

        Args:
            scene (str): Scene sentence body
            bad_instinct (str): Bad instinct sentence body
            first_move (str): First move sentence body

        Returns:
            scene (str): Compressed scene
            bad_instinct (str): Compressed bad instinct
            first_move (str): Compressed first move
        """
        variants = [
            (
                scene,
                bad_instinct,
                first_move,
            ),
            (
                scene.replace("right before", "before").replace("the first", "your first"),
                bad_instinct,
                first_move,
            ),
            (
                scene.replace("right before", "before").replace("the first", "your first").replace(" through nginx", ""),
                bad_instinct,
                first_move.split(",", 1)[0].strip(),
            ),
            (
                scene.replace("right before", "before").replace("the first", "your first").replace(" through nginx", ""),
                bad_instinct.replace("production readiness", "prod-ready"),
                first_move.split(",", 1)[0].strip(),
            ),
        ]

        for candidate_scene, candidate_bad_instinct, candidate_first_move in variants:
            candidate_tweet = ". ".join(
                [
                    part.rstrip(". ")
                    for part in (candidate_scene, candidate_bad_instinct, candidate_first_move)
                    if part
                ]
            ).strip()
            candidate_tweet = self._sanitize_tweet_render(candidate_tweet)
            if len(candidate_tweet) <= self._MAX_TWEET_LENGTH:
                return candidate_scene, candidate_bad_instinct, candidate_first_move

        return variants[-1]

    def _render_complete_tweet(self, scene: str, bad_instinct: str, first_move: str) -> tuple[str, bool]:
        """
        Renders a complete-sentence tweet from core slots only.

        Args:
            scene (str): Scene
            bad_instinct (str): Bad instinct
            first_move (str): First move

        Returns:
            tweet (str): Final tweet
            render_complete (bool): Whether the result kept complete sentence structure
        """
        scene, bad_instinct, first_move = self._compress_tweet_safely(
            scene,
            bad_instinct,
            first_move,
        )
        tweet = ". ".join(
            [
                part.rstrip(". ")
                for part in (scene, bad_instinct, first_move)
                if part
            ]
        ).strip()
        tweet = self._sanitize_tweet_render(tweet)
        render_complete = (
            bool(tweet)
            and len(tweet) <= self._MAX_TWEET_LENGTH
            and not tweet.endswith(" the")
            and not tweet.endswith(" to")
            and not tweet.endswith(" and")
            and not tweet.endswith(" or")
        )
        return tweet, render_complete

    def _generate_tweet_slots(self) -> dict:
        """
        Generates structured slots for final tweet rendering.

        Returns:
            slots (dict): Slot payload
        """
        completion = generate_text(
            f"""
            Generate slot JSON for a short technical X post.

            Topic / angle: {self.topic}
            {build_profile_context(self.content_profile)}
            Reusable case brief:
            {self.case_brief or "None"}
            Variant guidance:
            {self._variant_instruction()}
            Asset guidance:
            {self._asset_instruction()}
            Required field status:
            {build_required_field_status(self.content_profile)}

            Return valid JSON only with this schema:
            {{
              "scene": "short concrete moment before a real decision or exposure",
              "bad_instinct": "bad instinct, dangerous default, or common misjudgment",
              "first_move": "immediate action step",
              "optional_identity_cue": "",
              "optional_cta": ""
            }}

            Requirements:
            - scene must be concrete
            - bad_instinct must use one of these sentence forms:
              - the bad instinct is to ...
              - most builders assume ...
              - the risky default is to ...
              - the mistake is to ...
            - bad_instinct must describe a wrong idea or dangerous default, not a vague state, confusion, or consequence
            - first_move must start with one of: check, verify, inspect, list, compare, disable, trace, review
            - first_move must point to a deployment/config/product-internal action
            - first_move must not be a checklist, guide, template, or download action
            - optional_cta should default to empty
            - do not copy raw desired_identity, avoided_identity, or expected_attribute wording
            """
        )

        cleaned = completion.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)

    def _validate_tweet_slots(self, slots: dict) -> dict:
        """
        Validates slots against hard Twitter constraints.

        Args:
            slots (dict): Slot payload

        Returns:
            result (dict): Validation result
        """
        scene = str(slots.get("scene", "") or "").strip()
        bad_instinct = str(slots.get("bad_instinct", "") or "").strip()
        first_move = str(slots.get("first_move", "") or "").strip()
        optional_cta = str(slots.get("optional_cta", "") or "").strip()

        bad_instinct_valid, bad_instinct_reason = self._is_valid_bad_instinct(
            bad_instinct
        )

        return {
            "scene": scene,
            "bad_instinct": bad_instinct,
            "first_move": first_move,
            "optional_cta": optional_cta,
            "scene_valid": bool(scene),
            "bad_instinct_valid": bad_instinct_valid,
            "bad_instinct_reason": bad_instinct_reason,
            "first_move_valid": self._is_valid_first_move(first_move),
            "cta_shadow": self._contains_cta_shadow(optional_cta)
            or self._contains_cta_shadow(first_move),
            "expected_attribute_leak": self._contains_expected_attribute_leak(scene)
            or self._contains_expected_attribute_leak(bad_instinct)
            or self._contains_expected_attribute_leak(first_move),
        }

    def _sanitize_tweet_render(self, text: str) -> str:
        """
        Removes CTA shadows and expected-attribute leakage from final text.

        Args:
            text (str): Tweet draft

        Returns:
            cleaned (str): Sanitized tweet
        """
        cleaned = str(text or "").strip()
        patterns = [
            r"\\bclear first-pass deploy judgment\\b",
            r"\\bno obvious exposure\\b",
            r"\\bavoid deployment mistakes\\b",
            r"\\bsafer first release\\b",
            r"\\bdownload(?: now)?\\b.*",
            r"\\buse our checklist\\b.*",
            r"\\buse this checklist\\b.*",
        ]
        for pattern in patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r"\\s+", " ", cleaned).strip(" .,:;-")
        return cleaned

    def _render_tweet_from_slots(self, scene: str, bad_instinct: str, first_move: str) -> str:
        """
        Renders final tweet from core slots only.

        Args:
            scene (str): Concrete scene
            bad_instinct (str): Mistaken instinct
            first_move (str): Immediate action

        Returns:
            tweet (str): Final tweet
        """
        tweet, _ = self._render_complete_tweet(scene, bad_instinct, first_move)
        return tweet

    def _review_json_prompt(self, draft: str) -> str:
        """
        Builds the structured review prompt for X posts.

        Args:
            draft (str): Draft post text

        Returns:
            prompt (str): Review prompt
        """
        return f"""
            Review and improve this X post for a technical reusable-business-asset operator.

            Draft:
            {draft}

            Context:
            Topic / angle: {self.topic}
            {build_profile_context(self.content_profile)}
            Reusable case brief:
            {self.case_brief or "None"}
            Variant guidance:
            {self._variant_instruction()}
            Asset guidance:
            {self._asset_instruction()}
            Required field status:
            {build_required_field_status(self.content_profile)}
            Demand diagnostics:
            {self._demand_diagnostics_instruction()}
            Post mode:
            {self._tweet_mode_instruction()}
            Anti-field-hauling rule:
            {self._field_hauling_block()}
            {self._field_hauling_examples()}

            Return valid JSON only with this schema:
            {{
              "scene": "short scene phrase",
              "bad_instinct": "mistaken instinct or dangerous default",
              "first_move": "immediate action step",
              "identity_cue": "optional natural identity cue",
              "cta": "optional CTA",
              "final_post": "revised post",
              "checks": {{
                "scene_present": true,
                "blind_spot_present": true,
                "first_move_present": true,
                "expected_attribute_present": true,
                "cta_present": false,
                "cta_allowed": false,
                "field_hauling_detected": false
              }},
              "missing_items": ["blind_spot", "first_move"],
              "field_hauling_reasons": ["copied desired_identity wording"]
            }}

            Requirements:
            - Keep the core meaning
            - Remove hype, fluff, and generic AI phrasing
            - Preserve this strict priority order:
              1. scene
              2. mistaken instinct / blind spot
              3. first move
              4. natural identity cue only if room remains
              5. CTA only if all core elements survive
            - The blind spot must read like a bad instinct, dangerous default, or common misjudgment
            - The first move must be an immediate action, not a slogan, attitude, or download CTA
            - If space is tight, delete the CTA first, then identity cue
            - Never sacrifice blind spot or first move to keep a CTA
            - Explicitly check whether the post contains:
              1. a concrete scene
              2. a mistaken instinct / blind spot
              3. a first move
              4. the expected attribute or promised outcome
              5. any CTA
            - Explicitly check whether the draft copies any raw field wording from desired_identity, avoided_identity, or expected_attribute
            - CTA is allowed only when:
              scene_present = true
              blind_spot_present = true
              first_move_present = true
            - If CTA appears while blind_spot_present = false or first_move_present = false, set cta_allowed = false and rewrite without CTA
            - Keep the final post under {self._MAX_TWEET_LENGTH} characters
        """

    def _parse_review_result(self, reviewed: str, draft: str) -> tuple[str, dict, list[str], list[str]]:
        """
        Parses structured review output.

        Args:
            reviewed (str): Raw model response
            draft (str): Fallback draft

        Returns:
            final_post (str): Final reviewed post
            checks (dict): Structured checks
            missing_items (list[str]): Missing item list
            field_hauling_reasons (list[str]): Field hauling issues
        """
        cleaned = reviewed.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(cleaned)
        final_post = str(parsed.get("final_post", "")).replace('"', "").strip() or draft
        checks = parsed.get("checks", {}) or {}
        missing_items = [str(item) for item in (parsed.get("missing_items", []) or [])]
        field_hauling_reasons = [
            str(item) for item in (parsed.get("field_hauling_reasons", []) or [])
        ]
        return re.sub(r"\*", "", final_post), checks, missing_items, field_hauling_reasons

    def __init__(
        self,
        account_uuid: str,
        account_nickname: str,
        fp_profile_path: str,
        topic: str,
        content_profile: dict | None = None,
    ) -> None:
        """
        Initializes the Twitter Bot.

        Args:
            account_uuid (str): The account UUID
            account_nickname (str): The account nickname
            fp_profile_path (str): The path to the Firefox profile

        Returns:
            None
        """
        self.account_uuid: str = account_uuid
        self.account_nickname: str = account_nickname
        self.fp_profile_path: str = fp_profile_path
        self.topic: str = topic
        self.content_profile = normalize_content_profile(content_profile)
        self.case_brief = load_case_brief(self.content_profile)
        self.missing_required_fields = missing_required_strategy_fields(
            self.content_profile
        )

        # Initialize the Firefox profile
        self.options: Options = Options()

        # Set headless state of browser
        if get_headless():
            self.options.add_argument("--headless")

        if not os.path.isdir(fp_profile_path):
            raise ValueError(
                f"Firefox profile path does not exist or is not a directory: {fp_profile_path}"
            )

        # Set the profile path
        self.options.add_argument("-profile")
        self.options.add_argument(fp_profile_path)

        # Set the service
        self.service: Service = Service(GeckoDriverManager().install())

        # Initialize the browser
        self.browser: webdriver.Firefox = webdriver.Firefox(
            service=self.service, options=self.options
        )
        self.wait: WebDriverWait = WebDriverWait(self.browser, 30)

    def post(self, text: Optional[str] = None) -> None:
        """
        Starts the Twitter Bot.

        Args:
            text (str): The text to post

        Returns:
            None
        """
        bot: webdriver.Firefox = self.browser
        verbose: bool = get_verbose()

        bot.get("https://x.com/compose/post")

        post_content: str = text if text is not None else self.generate_post()
        now: datetime = datetime.now()

        print(colored(" => Posting to Twitter:", "blue"), post_content[:30] + "...")
        body = post_content

        text_box = None
        text_box_selectors = [
            (By.CSS_SELECTOR, "div[data-testid='tweetTextarea_0'][role='textbox']"),
            (By.XPATH, "//div[@data-testid='tweetTextarea_0']//div[@role='textbox']"),
            (By.XPATH, "//div[@role='textbox']"),
        ]

        for selector in text_box_selectors:
            try:
                text_box = self.wait.until(EC.element_to_be_clickable(selector))
                text_box.click()
                text_box.send_keys(body)
                break
            except Exception:
                continue

        if text_box is None:
            raise RuntimeError(
                "Could not find tweet text box. Ensure you are logged into X in this Firefox profile."
            )


        post_button = None
        post_button_selectors = [
            (By.XPATH, "//button[@data-testid='tweetButtonInline']"),
            (By.XPATH, "//button[@data-testid='tweetButton']"),
            (By.XPATH, "//span[text()='Post']/ancestor::button"),
        ]

        for selector in post_button_selectors:
            try:
                post_button = self.wait.until(EC.element_to_be_clickable(selector))
                post_button.click()
                break
            except Exception:
                continue

        if post_button is None:
            raise RuntimeError("Could not find the Post button on X compose screen.")

        if verbose:
            print(colored(" => Pressed [ENTER] Button on Twitter..", "blue"))
        time.sleep(2)

        # Add the post to the cache
        self.add_post({"content": body, "date": now.strftime("%m/%d/%Y, %H:%M:%S")})

        success("Posted to Twitter successfully!")

    def get_posts(self) -> List[dict]:
        """
        Gets the posts from the cache.

        Returns:
            posts (List[dict]): The posts
        """
        if not os.path.exists(get_twitter_cache_path()):
            # Create the cache file
            with open(get_twitter_cache_path(), "w") as file:
                json.dump({"accounts": []}, file, indent=4)

        with open(get_twitter_cache_path(), "r") as file:
            parsed = json.load(file)

            # Find our account
            accounts = parsed["accounts"]
            for account in accounts:
                if account["id"] == self.account_uuid:
                    posts = account["posts"]

                    if posts is None:
                        return []

                    # Return the posts
                    return posts

        return []

    def add_post(self, post: dict) -> None:
        """
        Adds a post to the cache.

        Args:
            post (dict): The post to add

        Returns:
            None
        """
        posts = self.get_posts()
        posts.append(post)

        with open(get_twitter_cache_path(), "r") as file:
            previous_json = json.loads(file.read())

            # Find our account
            accounts = previous_json["accounts"]
            for account in accounts:
                if account["id"] == self.account_uuid:
                    account["posts"].append(post)

            # Commit changes
            with open(get_twitter_cache_path(), "w") as f:
                f.write(json.dumps(previous_json))

    def generate_post(self) -> str:
        """
        Generates a post for the Twitter account based on the topic.

        Returns:
            post (str): The post
        """
        if has_service_strategy(self.content_profile):
            if self.missing_required_fields:
                warning(
                    "Missing required strategy fields for X generation: "
                    + ", ".join(self.missing_required_fields)
                    + ". Falling back to explicit downgrade logic.",
                    False,
                )
            validation = None
            for _attempt in range(3):
                slots = self._generate_tweet_slots()
                validation = self._validate_tweet_slots(slots)
                if (
                    validation["scene_valid"]
                    and validation["bad_instinct_valid"]
                    and validation["first_move_valid"]
                    and not validation["cta_shadow"]
                    and not validation["expected_attribute_leak"]
                ):
                    break

            if validation is None:
                completion = ""
            else:
                completion, render_complete = self._render_complete_tweet(
                    validation["scene"],
                    validation["bad_instinct"],
                    validation["first_move"],
                )
                if not render_complete:
                    warning("Rendered tweet was not complete after safe compression.", False)
        else:
            completion = generate_text(
                f"Generate a Twitter post about: {self.topic} in {get_twitter_language()}. "
                "The Limit is 2 sentences. Choose a specific sub-topic of the provided topic."
            )

        if get_verbose():
            info("Generating a post...")

        if completion is None:
            error("Failed to generate a post. Please try again.")
            sys.exit(1)

        # Apply Regex to remove all *
        completion = re.sub(r"\*", "", completion).replace('"', "")

        if has_service_strategy(self.content_profile):
            completion = self.review_post(completion)

        if get_verbose():
            info(f"Length of post: {len(completion)}")
        if len(completion) >= 260:
            return completion[:257].rsplit(" ", 1)[0] + "..."

        return completion

    def review_post(self, draft: str) -> str:
        """
        Reviews the generated post against service-led quality constraints.

        Args:
            draft (str): Initial generated post

        Returns:
            post (str): Reviewed post
        """
        reviewed = generate_text(self._review_json_prompt(draft))
        try:
            final_post, checks, missing_items, field_hauling_reasons = self._parse_review_result(
                reviewed, draft
            )
            blind_spot_present = bool(checks.get("blind_spot_present", False))
            first_move_present = bool(checks.get("first_move_present", False))
            cta_present = bool(checks.get("cta_present", False)) or self._cta_heuristic_present(final_post)
            cta_allowed = bool(checks.get("cta_allowed", False))
            field_hauling_detected = bool(checks.get("field_hauling_detected", False))
            if missing_items:
                warning(
                    "X review missing items: " + ", ".join(str(item) for item in missing_items),
                    False,
                )
            if field_hauling_detected:
                warning(
                    "X review detected field hauling: "
                    + ", ".join(str(item) for item in field_hauling_reasons),
                    False,
                )
            if cta_present and (not blind_spot_present or not first_move_present or not cta_allowed):
                warning(
                    "X review rejected CTA because it displaced blind_spot or first_move. Rewriting without CTA.",
                    False,
                )
                second_pass = generate_text(
                    self._review_json_prompt(
                        draft
                        + "\n\nRewrite rule: remove the CTA entirely and keep only scene + blind spot + first move."
                    )
                )
                second_post, _, second_missing, second_field_hauling = self._parse_review_result(
                    second_pass, final_post
                )
                if second_missing:
                    warning(
                        "X second-pass review missing items: "
                        + ", ".join(str(item) for item in second_missing),
                        False,
                    )
                if second_field_hauling:
                    warning(
                        "X second-pass field hauling: "
                        + ", ".join(str(item) for item in second_field_hauling),
                        False,
                    )
                return self._sanitize_tweet_render(second_post)
            return self._sanitize_tweet_render(final_post)
        except Exception:
            cleaned_post = re.sub(r"\*", "", reviewed).replace('"', "").strip()
            warning(
                "X review did not return structured checks. Falling back to reviewed text.",
                False,
            )
            return self._sanitize_tweet_render(cleaned_post or draft)
