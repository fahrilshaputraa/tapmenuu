document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('[data-theme-form]');
  const phone = document.querySelector('[data-preview-phone]');

  const resetTrigger = document.querySelector('[data-reset-theme-trigger]');
  const resetModal = document.querySelector('[data-reset-theme-modal]');
  const resetPanel = document.querySelector('[data-reset-theme-panel]');
  const resetCancel = document.querySelector('[data-reset-theme-cancel]');

  function openResetModal() {
    if (!resetModal) return;
    resetModal.classList.remove('hidden');
    resetModal.classList.add('flex');
    document.body.classList.add('overflow-hidden');
    resetCancel?.focus();
  }

  function closeResetModal() {
    if (!resetModal) return;
    resetModal.classList.add('hidden');
    resetModal.classList.remove('flex');
    document.body.classList.remove('overflow-hidden');
    resetTrigger?.focus();
  }

  resetTrigger?.addEventListener('click', openResetModal);
  resetCancel?.addEventListener('click', closeResetModal);
  resetModal?.addEventListener('click', function (event) {
    if (event.target === resetModal) closeResetModal();
  });
  resetPanel?.addEventListener('click', function (event) {
    event.stopPropagation();
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && resetModal && !resetModal.classList.contains('hidden')) {
      closeResetModal();
    }
  });

  if (!form || !phone) return;

  const fieldToVar = {
    primary_color: '--preview-primary',
    secondary_color: '--preview-secondary',
    accent_color: '--preview-accent',
    background_color: '--preview-bg',
    text_color: '--preview-text',
    card_color: '--preview-card',
  };

  const header = phone.querySelector('[data-preview-header]');
  const tabs = phone.querySelector('[data-preview-tabs]');
  const list = phone.querySelector('[data-preview-list]');
  const button = phone.querySelector('.preview-button');
  const previewTagline = phone.querySelector('[data-preview-tagline]');
  const previewGreeting = phone.querySelector('[data-preview-greeting]');
  const previewReceipt = phone.querySelector('[data-preview-receipt]');
  const previewRestaurant = phone.querySelector('[data-preview-restaurant]');

  // Banner preview - one-time listener (file -> preview)
  const bannerInput = form.querySelector('[name="banner_image"]');
  const previewBanner = phone.querySelector('[data-preview-banner]');
  const previewBannerImg = phone.querySelector('[data-preview-banner-img]');
  if (bannerInput && previewBanner && previewBannerImg) {
    bannerInput.addEventListener('change', function () {
      if (bannerInput.files && bannerInput.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
          previewBannerImg.src = e.target.result;
          previewBannerImg.classList.remove('hidden');
          previewBanner.classList.remove('hidden');
        };
        reader.readAsDataURL(bannerInput.files[0]);
      }
    });
  }

  function applyPreview() {
    Object.entries(fieldToVar).forEach(([fieldName, cssVar]) => {
      const input = form.querySelector(`[name="${fieldName}"]`);
      if (input && input.value) {
        phone.style.setProperty(cssVar, input.value);
        const hexLabel = form.querySelector(`[data-hex-for="${fieldName}"]`);
        if (hexLabel) hexLabel.textContent = input.value.toUpperCase();
      }
    });

    const font = form.querySelector('[name="font_family"]')?.value || 'Plus Jakarta Sans';
    phone.style.fontFamily = `'${font}', sans-serif`;

    const layout = form.querySelector('[name="layout_style"]')?.value || 'grid';
    const headerStyle = form.querySelector('[name="header_style"]')?.value || 'rounded';
    const buttonStyle = form.querySelector('[name="button_style"]')?.value || 'rounded';
    const showTabs = form.querySelector('[name="show_category_tabs"]')?.checked ?? true;

    list?.setAttribute('data-layout-style', layout);
    header?.setAttribute('data-header-style', headerStyle);
    button?.setAttribute('data-button-style', buttonStyle);
    tabs?.classList.toggle('hidden', !showTabs);

    // Text live — tagline fallback to restaurant.description (mirrors customer_menu)
    const taglineInput = form.querySelector('[name="tagline"]');
    if (previewTagline && taglineInput) {
      const val = taglineInput.value.trim();
      const fallback = previewTagline.getAttribute('data-fallback-description')?.trim() || '';
      if (val) {
        previewTagline.textContent = val;
        previewTagline.classList.remove('hidden');
      } else if (fallback) {
        // show fallback description truncated like customer_menu does
        const words = fallback.split(/\s+/).slice(0, 12).join(' ');
        previewTagline.textContent = words;
        previewTagline.classList.remove('hidden');
      } else {
        previewTagline.textContent = '';
        previewTagline.classList.add('hidden');
      }
    }
    const greetingInput = form.querySelector('[name="greeting_message"]');
    if (previewGreeting && greetingInput) {
      const val = greetingInput.value.trim();
      if (val) {
        previewGreeting.textContent = val;
        previewGreeting.classList.remove('hidden');
      } else {
        previewGreeting.textContent = '';
        previewGreeting.classList.add('hidden');
      }
    }
    const receiptInput = form.querySelector('[name="receipt_footer_text"]');
    if (previewReceipt && receiptInput) {
      const val = receiptInput.value.trim();
      previewReceipt.textContent = val;
      previewReceipt.classList.toggle('hidden', !val);
    }
    // Contacts live
    const contactPhoneInput = form.querySelector('[name="contact_phone"]');
    const contactIgInput = form.querySelector('[name="contact_instagram"]');
    const previewContacts = phone.querySelector('[data-preview-contacts]');
    const previewPhoneText = phone.querySelector('[data-preview-phone-text]');
    const previewIgText = phone.querySelector('[data-preview-ig-text]');
    const previewFooterContacts = phone.querySelector('[data-preview-contacts-footer]');
    const previewFooterPhone = phone.querySelector('[data-preview-footer-phone]');
    const previewFooterIg = phone.querySelector('[data-preview-footer-ig]');
    if (previewContacts) {
      const phoneVal = contactPhoneInput?.value.trim() || '';
      const igVal = contactIgInput?.value.trim() || '';
      const hasContact = !!(phoneVal || igVal);
      previewContacts.classList.toggle('hidden', !hasContact);
      if (previewPhoneText) {
        if (phoneVal) {
          previewPhoneText.textContent = ' ' + phoneVal;
          previewPhoneText.classList.remove('hidden');
          previewPhoneText.previousElementSibling?.classList?.remove('hidden');
        } else {
          previewPhoneText.classList.add('hidden');
        }
        // update inner icon + text - keep icon and text baseline aligned
        previewPhoneText.innerHTML = phoneVal ? '<i class="fa-solid fa-phone text-[9px] leading-none shrink-0"></i><span class="leading-none">' + phoneVal + '</span>' : '';
        if (phoneVal) previewPhoneText.classList.remove('hidden');
        else previewPhoneText.classList.add('hidden');
      }
      if (previewIgText) {
        previewIgText.innerHTML = igVal ? '<i class="fa-brands fa-instagram text-[9px] leading-none shrink-0"></i><span class="leading-none">@' + igVal + '</span>' : '';
        if (igVal) previewIgText.classList.remove('hidden');
        else previewIgText.classList.add('hidden');
      }
      if (previewFooterContacts) {
        previewFooterContacts.classList.toggle('hidden', !hasContact);
        if (previewFooterPhone) previewFooterPhone.textContent = phoneVal || '';
        if (previewFooterIg) previewFooterIg.textContent = igVal ? (phoneVal ? ' • @' + igVal : '@' + igVal) : '';
      }
    }
    // Visual card selected states
    document.querySelectorAll('[data-visual-group]').forEach((group) => {
      const field = group.getAttribute('data-visual-group');
      const select = form.querySelector(`[name="${field}"]`);
      const current = select?.value;
      group.querySelectorAll('[data-visual-value]').forEach((card) => {
        const isActive = card.getAttribute('data-visual-value') === current;
        card.classList.toggle('border-primary', isActive);
        card.classList.toggle('bg-secondary/30', isActive);
        card.classList.toggle('shadow-sm', isActive);
        card.classList.toggle('border-gray-200', !isActive);
      });
    });

    // Palette selected state — match by primary+accent+text for uniqueness (18 palettes)
    const primaryVal = form.querySelector('[name="primary_color"]')?.value?.toLowerCase();
    const accentVal = form.querySelector('[name="accent_color"]')?.value?.toLowerCase();
    document.querySelectorAll('.palette-card').forEach((card) => {
      const p = card.getAttribute('data-primary')?.toLowerCase();
      const a = card.getAttribute('data-accent')?.toLowerCase();
      const isMatch = p === primaryVal && a === accentVal;
      // fallback: if accent identical (e.g. edited manually), match primary only
      const fallbackMatch = !isMatch && p === primaryVal && document.querySelectorAll('.palette-card[data-primary="' + card.getAttribute('data-primary') + '"]').length === 1;
      const finalMatch = isMatch || fallbackMatch;
      card.classList.toggle('border-primary', finalMatch);
      card.classList.toggle('ring-2', finalMatch);
      card.classList.toggle('ring-primary/20', finalMatch);
      card.classList.toggle('shadow-md', finalMatch);
      card.classList.toggle('border-gray-200', !finalMatch);
      if (finalMatch) card.setAttribute('data-selected', 'true');
      else card.removeAttribute('data-selected');
    });
  }

  // Palette click -> fill 6 colors (now includes text_color for curated harmony)
  document.querySelectorAll('.palette-card').forEach((card) => {
    card.addEventListener('click', function () {
      const mapping = {
        primary_color: card.getAttribute('data-primary'),
        secondary_color: card.getAttribute('data-secondary'),
        accent_color: card.getAttribute('data-accent'),
        background_color: card.getAttribute('data-bg'),
        card_color: card.getAttribute('data-card'),
        text_color: card.getAttribute('data-text'),
      };
      Object.entries(mapping).forEach(([field, val]) => {
        if (!val) return;
        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
          input.value = val;
          input.dispatchEvent(new Event('input', { bubbles: true }));
        }
      });
      applyPreview();
      // scroll preview into view on mobile
      if (window.innerWidth < 1280) {
        document.querySelector('[data-preview-phone]')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Visual cards click -> update hidden select
  document.querySelectorAll('[data-visual-value]').forEach((card) => {
    card.addEventListener('click', function () {
      const field = card.getAttribute('data-visual-field');
      const value = card.getAttribute('data-visual-value');
      const select = form.querySelector(`[name="${field}"]`);
      if (select) {
        select.value = value;
        select.dispatchEvent(new Event('change', { bubbles: true }));
      }
      applyPreview();
    });
  });

  form.addEventListener('input', applyPreview);
  form.addEventListener('change', applyPreview);
  applyPreview();

  // Keyboard focus visible
  form.addEventListener('focusin', function (e) {
    if (e.target.matches('input, select, textarea')) {
      e.target.classList.add('ring-2', 'ring-primary/20');
    }
  });
});
