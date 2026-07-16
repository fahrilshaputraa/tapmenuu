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

  function applyPreview() {
    Object.entries(fieldToVar).forEach(([fieldName, cssVar]) => {
      const input = form.querySelector(`[name="${fieldName}"]`);
      if (input && input.value) phone.style.setProperty(cssVar, input.value);
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
  }

  form.addEventListener('input', applyPreview);
  form.addEventListener('change', applyPreview);
  applyPreview();
});
