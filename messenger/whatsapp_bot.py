"""
WhatsApp Web Automation Bot using Selenium

This module handles the automation of sending messages through WhatsApp Web.
"""

import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class WhatsAppBot:
    """Controls WhatsApp Web via Selenium for automated messaging."""
    
    # Default country code for Mexico
    DEFAULT_COUNTRY_CODE = "52"
    
    # Delays between messages (in seconds) to avoid detection
    MIN_DELAY = 2
    MAX_DELAY = 4
    
    def __init__(self, profile_dir=None):
        """
        Initialize the WhatsApp bot.
        
        Args:
            profile_dir: Directory to store Chrome profile for session persistence
        """
        self.driver = None
        self.profile_dir = profile_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'chrome_profile'
        )
        
    def start(self):
        """Start the Chrome browser with WhatsApp Web."""
        options = Options()
        
        # Use a persistent profile to save login session
        options.add_argument(f"--user-data-dir={self.profile_dir}")
        
        # Disable automation flags to avoid detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Additional options for stability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Initialize driver with auto-managed ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Navigate to WhatsApp Web
        self.driver.get("https://web.whatsapp.com")
        
        return True
    
    def is_active(self):
        """Check if the browser driver is still active and responsive."""
        if not self.driver:
            return False
        try:
            # Try to get the title to see if browser is still responsive
            _ = self.driver.title
            return True
        except Exception:
            return False
    
    def wait_for_login(self, timeout=120):
        """
        Wait for the user to scan QR code and login.
        
        Args:
            timeout: Maximum seconds to wait for login
            
        Returns:
            True if logged in, False if timeout
        """
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            try:
                # Check for multiple indicators of successful login
                indicators = [
                    '[data-icon="menu"]',               # Menu icon (3 dots)
                    '[data-icon="chat"]',               # New chat icon
                    '[data-icon="new-chat-outline"]',   # New chat outline
                    '#pane-side',                       # Chat list pane
                    'div[data-testid="chat-list-search"]', # Search box
                    'div[id="side"]',                   # Side panel
                ]
                
                for selector in indicators:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if element and element.is_displayed():
                            time.sleep(2)  # Extra wait for full load
                            return True
                    except Exception:
                        continue
                
                # If checking closely, we might want a small sleep
                time.sleep(1)
                
            except Exception:
                time.sleep(1)
                
        return False
    
    def normalize_phone(self, phone):
        """
        Normalize phone number to include country code.
        
        Args:
            phone: Phone number (may or may not include country code)
            
        Returns:
            Normalized phone number with country code, digits only
        """
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, str(phone)))
        
        # If the number doesn't start with country code, add Mexico's
        if len(digits) == 10:
            digits = self.DEFAULT_COUNTRY_CODE + digits
        elif not digits.startswith(self.DEFAULT_COUNTRY_CODE) and len(digits) < 12:
            digits = self.DEFAULT_COUNTRY_CODE + digits
            
        return digits

    def _first_displayed(self, elements):
        """Return the first displayed element from a list, else None."""
        for el in elements or []:
            try:
                if el and el.is_displayed():
                    return el
            except Exception:
                continue
        return None

    def _coerce_click_target(self, el):
        """
        If `el` is an icon/span, try to find a clickable ancestor (button or role=button).
        Otherwise return `el`.
        """
        if el is None:
            return None
        try:
            tag = (el.tag_name or "").lower()
        except Exception:
            tag = ""

        if tag in {"span", "svg", "path"}:
            # Prefer a real <button>, otherwise a role=button container.
            for xpath in ("./ancestor::button[1]", "./ancestor::*[@role='button'][1]"):
                try:
                    anc = el.find_element(By.XPATH, xpath)
                    if anc:
                        return anc
                except Exception:
                    continue
        return el

    def _safe_click(self, el):
        """Click with fallbacks for intercepted/overlayed elements."""
        if el is None:
            return False
        try:
            el.click()
            return True
        except Exception:
            try:
                # JS click as a fallback when normal click is intercepted.
                self.driver.execute_script("arguments[0].click();", el)
                return True
            except Exception:
                return False

    def dismiss_notifications(self):
        """
        Dismiss any notification popups or overlays that might interfere with bot actions.
        This helps prevent incoming messages from blocking UI interactions.
        """
        try:
            # Common notification/popup close button selectors
            close_selectors = [
                # Generic close buttons
                'span[data-icon="x"]',
                'span[data-icon="x-viewer"]',
                'button[aria-label="Close"]',
                'button[aria-label="Cerrar"]',
                # Notification drawer close
                'div[data-testid="popup-controls-close"]',
                # Alert/dialog dismiss buttons
                'div[role="dialog"] button[aria-label="OK"]',
                'div[role="dialog"] button[aria-label="Aceptar"]',
                'div[role="alertdialog"] button',
            ]
            
            for selector in close_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for el in elements:
                        if el and el.is_displayed():
                            self._safe_click(el)
                            time.sleep(0.2)
                except Exception:
                    continue
            
            # Also try to close any overlay by clicking outside it
            try:
                overlays = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-animate-modal-backdrop="true"]')
                for overlay in overlays:
                    if overlay and overlay.is_displayed():
                        # Press Escape to close modal
                        from selenium.webdriver.common.keys import Keys
                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        time.sleep(0.3)
                        break
            except Exception:
                pass
                
        except Exception:
            pass  # Don't let notification handling break the main flow

    def _ensure_chat_focus(self):
        """
        Ensure we're focused on the current chat and not distracted by notifications.
        Call this before critical actions like sending messages.
        """
        try:
            # Dismiss any popups first
            self.dismiss_notifications()
            
            # Click on the main chat area to ensure focus
            main_selectors = [
                '#main',
                'div[data-testid="conversation-panel-wrapper"]',
                'footer',
            ]
            
            for selector in main_selectors:
                try:
                    main_area = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if main_area and main_area.is_displayed():
                        # Don't click directly, just ensure it exists
                        return True
                except Exception:
                    continue
                    
            return True
        except Exception:
            return False

    def _retry_on_stale(self, action_fn, max_retries=3):
        """
        Retry an action if it fails due to stale element reference.
        
        Args:
            action_fn: A callable that performs the action
            max_retries: Maximum number of retry attempts
            
        Returns:
            Result of action_fn if successful, None if all retries failed
        """
        from selenium.common.exceptions import StaleElementReferenceException
        
        for attempt in range(max_retries):
            try:
                return action_fn()
            except StaleElementReferenceException:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
                else:
                    return None
            except Exception as e:
                # For other exceptions, don't retry
                raise e
        return None

    def _find_preview_send_button(self, timeout=30):
        """
        Find the send button in the attachment preview.
        Returns a clickable element or None.
        """
        end = time.time() + max(1, int(timeout))

        # Prefer searching within a dialog if present to avoid matching the main chat send button.
        def get_search_roots():
            try:
                dialogs = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="dialog"]')
                roots = [d for d in dialogs if d.is_displayed()]
                return roots if roots else [self.driver]
            except Exception:
                return [self.driver]

        css_selectors = [
            # Common modern WhatsApp send button testid
            'button[data-testid="compose-btn-send"]',
            'button[data-testid="send"]',
            'span[data-testid="send"]',
            # Aria-labels
            'button[aria-label="Send"]',
            'button[aria-label="Enviar"]',
            'div[role="button"][aria-label="Send"]',
            'div[role="button"][aria-label="Enviar"]',
            # Icon-based (we will coerce ancestor)
            'button span[data-icon="send"]',
            'span[data-icon="send"]',
        ]

        xpath_selectors = [
            # Button/div containing a send icon span
            ".//button[.//span[@data-icon='send']]",
            ".//*[@role='button'][.//span[@data-icon='send']]",
            # Some UIs use svg without span; match by aria-label on container
            ".//button[@aria-label='Send' or @aria-label='Enviar']",
            ".//*[@role='button'][@aria-label='Send' or @aria-label='Enviar']",
        ]
        driver_xpath_selectors = [
            # Same as above but absolute for driver-level searches
            "//button[.//span[@data-icon='send']]",
            "//*[@role='button'][.//span[@data-icon='send']]",
            "//button[@aria-label='Send' or @aria-label='Enviar']",
            "//*[@role='button'][@aria-label='Send' or @aria-label='Enviar']",
        ]

        while time.time() < end:
            roots = get_search_roots()
            for root in roots:
                for selector in css_selectors:
                    try:
                        els = root.find_elements(By.CSS_SELECTOR, selector) if root is not self.driver else self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for el in els:
                            target = self._coerce_click_target(el)
                            try:
                                if target and target.is_displayed() and target.is_enabled():
                                    return target
                            except Exception:
                                continue
                    except Exception:
                        continue

                for selector in xpath_selectors:
                    try:
                        if root is self.driver:
                            els = self.driver.find_elements(By.XPATH, driver_xpath_selectors[xpath_selectors.index(selector)])
                        else:
                            els = root.find_elements(By.XPATH, selector)
                        for el in els:
                            target = self._coerce_click_target(el)
                            try:
                                if target and target.is_displayed() and target.is_enabled():
                                    return target
                            except Exception:
                                continue
                    except Exception:
                        continue

            time.sleep(0.5)

        return None
    
    def send_message(self, phone, message, attachment_path=None):
        """
        Send a message to a phone number via WhatsApp Web.
        
        Args:
            phone: Phone number to send to
            message: Text message to send
            attachment_path: Optional path to file to attach
            
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        try:
            normalized_phone = self.normalize_phone(phone)
            message = "" if message is None else str(message)
            
            # Navigate directly to chat using wa.me link
            self.driver.get(f"https://web.whatsapp.com/send?phone={normalized_phone}")
            
            # Wait for the chat to load (message input box appears)
            try:
                message_box = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        'div[contenteditable="true"][data-tab="10"]'
                    ))
                )
            except Exception:
                # Check if there's an "invalid phone" popup
                try:
                    invalid_popup = self.driver.find_element(
                        By.XPATH, 
                        "//*[contains(text(), 'Phone number shared via url is invalid')]"
                    )
                    if invalid_popup:
                        return False, f"Invalid phone number: {phone}"
                except Exception:
                    pass
                return False, "Could not load chat - phone may not have WhatsApp"
            
            time.sleep(1)  # Brief pause for stability
            
            # Dismiss any notifications that might have appeared
            self.dismiss_notifications()
            self._ensure_chat_focus()
            
            # If there's an attachment, send it first
            if attachment_path and os.path.exists(attachment_path):
                try:
                    # Dismiss any popups before starting attachment flow
                    self.dismiss_notifications()
                    
                    abs_attachment_path = os.path.abspath(attachment_path)
                    attachment_ext = os.path.splitext(abs_attachment_path)[1].lower()
                    caption_typed = False
                    
                    # Step 1: Click the attach button
                    attach_btn = None
                    attach_selectors = [
                        'span[data-icon="clip"]',  # Classic WhatsApp UI (prioritize)
                        'span[data-icon="plus"]',  # New WhatsApp UI icon
                        'span[data-icon="attach-menu-plus"]',  # Alternative icon
                        'button[aria-label="Adjuntar"]',  # Spanish UI
                        'button[aria-label="Attach"]',  # English UI
                        'div[title="Attach"]',  # Title attribute
                        'div[title="Adjuntar"]',  # Spanish title
                    ]
                    
                    for selector in attach_selectors:
                        try:
                            attach_btn = WebDriverWait(self.driver, 2).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            if attach_btn:
                                break
                        except Exception:
                            continue
                    
                    if not attach_btn:
                        return False, f"Attachment failed at attach_button: could not find attach button (ext={attachment_ext})"
                    
                    # Click using JavaScript to avoid any event handler side effects
                    self._safe_click(attach_btn)
                    time.sleep(1)
                    
                    # Step 1.5: Click on "Document" menu item
                    # This step is CRITICAL: the file input might not be active/reachable until this is clicked.
                    doc_menu_item = None
                    doc_selectors = [
                        '//span[contains(text(), "Documento")]',
                        '//span[contains(text(), "Document")]',
                        'li[data-animate-dropdown-item="true"]:first-child',
                    ]
                    
                    # Try to find and click the document item
                    for selector in doc_selectors:
                        try:
                            if selector.startswith('//'):
                                doc_menu_item = WebDriverWait(self.driver, 2).until(
                                    EC.element_to_be_clickable((By.XPATH, selector))
                                )
                            else:
                                doc_menu_item = WebDriverWait(self.driver, 2).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                )
                            if doc_menu_item:
                                break
                        except Exception:
                            continue
                    
                    if doc_menu_item:
                        self._safe_click(doc_menu_item)
                        time.sleep(1)
                    else:
                        # Fallback: simple wait if we couldn't find the menu item (maybe UI changed again?)
                        # But usually, if we don't click this, file input won't work.
                        print("Warning: Could not find 'Document' menu item. Trying to proceed anyway.")
                        time.sleep(1)
                    
                    # Wait for file inputs to appear in the DOM
                    try:
                        WebDriverWait(self.driver, 5).until(
                            lambda d: len(d.find_elements(By.CSS_SELECTOR, 'input[type="file"]')) > 0
                        )
                    except Exception:
                        pass
                    
                    # Step 2: Find the DOCUMENT file input specifically using XPath.
                    # WhatsApp has multiple file inputs - we need accept="*" for documents.
                    file_input = None
                    
                    # Try XPath first (most reliable based on documentation)
                    try:
                        file_input = self.driver.find_element(By.XPATH, '//input[@accept="*"]')
                    except Exception:
                        pass
                    
                    # Fallback: find all inputs and filter
                    if not file_input:
                        try:
                            all_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
                            for inp in all_inputs:
                                accept = inp.get_attribute('accept') or ''
                                if accept == '*':
                                    file_input = inp
                                    break
                            # If no accept="*", use one that's not for images
                            if not file_input:
                                for inp in all_inputs:
                                    accept = inp.get_attribute('accept') or ''
                                    if 'image' not in accept.lower() and 'video' not in accept.lower():
                                        file_input = inp
                                        break
                            # Last resort
                            if not file_input and all_inputs:
                                file_input = all_inputs[0]
                        except Exception:
                            pass
                    
                    if not file_input:
                        return False, f"Attachment failed at file_input: could not find file input (ext={attachment_ext})"
                    
                    # Use JavaScript to set the file, which is more reliable and won't trigger click handlers
                    # First, make sure the input is not hidden in a way that prevents interaction
                    try:
                        self.driver.execute_script("""
                            arguments[0].style.display = 'block';
                            arguments[0].style.visibility = 'visible';
                            arguments[0].style.opacity = '1';
                        """, file_input)
                    except Exception:
                        pass
                    
                    # Send file path directly to the input element
                    file_input.send_keys(abs_attachment_path)
                    
                    # Dispatch change/input events to trigger WhatsApp's React handlers
                    try:
                        self.driver.execute_script("""
                            var event = new Event('change', { bubbles: true });
                            arguments[0].dispatchEvent(event);
                            var inputEvent = new Event('input', { bubbles: true });
                            arguments[0].dispatchEvent(inputEvent);
                        """, file_input)
                    except Exception:
                        pass
                    
                    time.sleep(2)

                    # Wait for attachment preview to appear (caption box and/or send button)
                    preview_timeout = 30

                    # Step 4: Add Caption (The Message)
                    # Only target real caption boxes; avoid generic contenteditable matches.
                    caption_box = None
                    caption_selectors = [
                        'div[aria-placeholder="Añade un comentario..."]',
                        'div[aria-placeholder="Add a caption..."]',
                        'div[role="textbox"][aria-placeholder="Añade un comentario..."]',
                        'div[role="textbox"][aria-placeholder="Add a caption..."]',
                    ]

                    # Explicit wait: either caption box or send button shows up
                    try:
                        WebDriverWait(self.driver, preview_timeout).until(
                            lambda d: any(d.find_elements(By.CSS_SELECTOR, s) for s in caption_selectors)
                            or self._find_preview_send_button(timeout=1) is not None
                        )
                    except Exception:
                        return False, f"Attachment failed at preview_open: timed out after {preview_timeout}s (ext={attachment_ext})"

                    # Try to find a caption box and type the message
                    for sel in caption_selectors:
                        try:
                            candidates = self.driver.find_elements(By.CSS_SELECTOR, sel)
                            caption_box = self._first_displayed(candidates)
                            if caption_box:
                                break
                        except Exception:
                            continue

                    if caption_box:
                        try:
                            caption_box.click()
                            time.sleep(0.2)
                            lines = str(message).split("\n")
                            for idx, line in enumerate(lines):
                                caption_box.send_keys(line)
                                if idx < len(lines) - 1:
                                    caption_box.send_keys(Keys.SHIFT + Keys.ENTER)
                            caption_typed = bool(message.strip())
                        except Exception:
                            # Caption is optional; continue to send without caption if it fails.
                            caption_box = None
                            caption_typed = False

                    # Step 5: Click Send (robustly) - wait until the preview send button is clickable/enabled
                    send_btn = self._find_preview_send_button(timeout=preview_timeout)
                    clicked_send = self._safe_click(send_btn) if send_btn else False

                    if not clicked_send:
                        # Fallback: send Enter to the caption box (best) or to the active element.
                        try:
                            if caption_box:
                                caption_box.send_keys(Keys.ENTER)
                            else:
                                active = self.driver.switch_to.active_element
                                active.send_keys(Keys.ENTER)
                            time.sleep(0.5)
                        except Exception as e:
                            return False, f"Attachment failed at preview_send: could not click send or press Enter (ext={attachment_ext}, err={str(e)})"
                    
                    # Wait for upload/send completion
                    time.sleep(3)
                    # If we successfully typed a caption, that's the text message content.
                    # Avoid sending a duplicate standalone text message.
                    if caption_typed:
                        return True, None
                    # Otherwise, fall through and send `message` as a separate chat message.
                    
                except Exception as e:
                    return False, f"Attachment failed: {str(e)}"
            
            # --- Send standalone text message (either no attachment, or attachment had no caption) ---
            if not message.strip():
                # Nothing to send as text.
                return True, None
            
            # Dismiss any notifications before sending text message
            self.dismiss_notifications()
            self._ensure_chat_focus()
            
            # Now send the text message
            # Re-find message box in case page changed
            message_box = None
            message_box_selectors = [
                'div[contenteditable="true"][data-tab="10"]',
                'div[contenteditable="true"][data-tab="6"]',  # Sometimes tab index changes
                '#main footer div[contenteditable="true"]',
                'div[aria-placeholder="Escribe un mensaje aquí"]',  # Spanish
                'div[aria-placeholder="Type a message"]',  # English
            ]
            
            for selector in message_box_selectors:
                try:
                    message_box = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if message_box:
                        break
                except Exception:
                    continue
            
            if not message_box:
                return False, "Could not find text message input box"
            
            # Type the message
            message_box.click()
            time.sleep(0.5)
            
            # Handle multi-line messages
            for line in message.split('\n'):
                message_box.send_keys(line)
                message_box.send_keys(Keys.SHIFT + Keys.ENTER)
            
            time.sleep(0.5)
            
            # Dismiss any last-minute notifications before sending
            self.dismiss_notifications()
            
            # Send the message
            # Method 1: Press Enter
            message_box.send_keys(Keys.ENTER)
            
            # Method 2: Click send button (fallback if Enter doesn't work)
            try:
                # Brief wait to see if message clears (indicating sent)
                time.sleep(1)
                if message_box.text.strip():
                    # Message still there, try clicking send button
                    self.dismiss_notifications()  # Clear any popups blocking send
                    send_btn = None
                    send_selectors = [
                        'span[data-icon="send"]',
                        'div[aria-label="Enviar"]',
                        'div[aria-label="Send"]',
                        'button[aria-label="Enviar"]',
                        'button[aria-label="Send"]',
                    ]
                    
                    for selector in send_selectors:
                        try:
                            send_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if send_btn:
                                send_btn.click()
                                break
                        except Exception:
                            continue
            except Exception:
                pass  # Ignore errors in fallback method
            
            # Wait a moment to confirm message was sent
            time.sleep(2)
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def random_delay(self):
        """Apply a random delay between messages to avoid detection."""
        delay = random.uniform(self.MIN_DELAY, self.MAX_DELAY)
        time.sleep(delay)
    
    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
