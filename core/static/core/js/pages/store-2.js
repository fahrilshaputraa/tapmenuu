function saveStoreProfile() {
            const btn = document.querySelector('button[onclick="saveStoreProfile()"]');
            const originalContent = btn.innerHTML;

            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Menyimpan...';
            btn.classList.add('opacity-75', 'cursor-not-allowed');

            setTimeout(() => {
                btn.innerHTML = '<i class="fa-solid fa-check"></i> Tersimpan';
                btn.classList.remove('bg-primary', 'hover:bg-primaryLight');
                btn.classList.add('bg-green-600');

                setTimeout(() => {
                    btn.innerHTML = originalContent;
                    btn.classList.remove('opacity-75', 'cursor-not-allowed', 'bg-green-600');
                    btn.classList.add('bg-primary', 'hover:bg-primaryLight');
                }, 2000);
            }, 1000);
        }

        function previewImage(input, imgId, placeholderId = null) {
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    const img = document.getElementById(imgId);
                    img.src = e.target.result;
                    img.classList.remove('hidden');

                    if (placeholderId) {
                        document.getElementById(placeholderId).classList.add('hidden');
                    }
                }
                reader.readAsDataURL(input.files[0]);
            }
        }
