$(document).ready(function () {
    $('#allocation-table').DataTable({
        "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "pageLength": -1,
        buttons: [
            {
                extend: 'colvis',
                columns: ':not(.exclude-export)'
            },
            'pageLength',
            // 'csv',
            'excel',
            // 'pdf',
            'print'
            ],
            dom: 'Bfrtip',
            // fixedHeader: true,
            // scrollX : true,
            // responsive: true,
            initComplete: function () {
            var table = this;
            this.api().columns().every(function () {
                var column = this;
                var header = $(column.header());
                var originalHeaderText = header.text();
                header.empty();

                var headerContainer = $('<div class="header-container"></div>').appendTo(header);
                $('<div class="header-text">' + originalHeaderText + '</div>').appendTo(headerContainer);
                var input = $('<input type="text" placeholder="Search ' + originalHeaderText + '">')
                    .appendTo(headerContainer)
                    .on('mousedown', function(e) {
                        // Prevent DataTables from capturing mousedown event
                        e.stopPropagation();
                    })
                    .on('keydown', function(e) {
                        // Handle Ctrl+A (or Cmd+A for Mac)
                        if ((e.ctrlKey || e.metaKey) && e.keyCode === 65) {
                            e.stopPropagation();
                            const self = this;
                            setTimeout(function() {
                                self.select();
                            }, 0);
                            return true;
                        }
                    })
                    .on('click', function(e) {
                        // Prevent event bubbling
                        e.stopPropagation();
                    })
                    .on('keyup', function (e) {
                        // Prevent keyup event from bubbling if it's part of Ctrl+A
                        if ((e.ctrlKey || e.metaKey) && e.keyCode === 65) {
                            e.stopPropagation();
                            return;
                        }
                        const searchTerms = $(this).val().trim();
                        const pattern = searchTerms.length ? searchTerms : '';
                        column
                            .search(pattern, true, false)
                            .draw();
                    });
            });
        }
    });

    // Prevent DataTables from capturing keyboard events globally
    $(document).off('keydown.dtb');
});

// Fungsi untuk memeriksa apakah nilai adalah angka
function isValidNumber(value) {
    return /^[0-9]*$/.test(value) || value === "";
}

// Menambahkan event listener untuk tombol "Simpan"
const saveButtons = document.querySelectorAll(".save-button");
saveButtons.forEach((button) => {
    button.addEventListener("click", () => {
        // Ambil elemen baris yang berisi tombol "Simpan" yang diklik
        const row = button.closest("tr");

        // Ambil data yang ingin Anda simpan dari elemen baris
        const computeName = row.querySelector(".computeName").textContent.trim();
        const cpuInput = row.querySelector(".cpu-input");
        const ramInput = row.querySelector(".ram-input");
        const keteranganInput = row.querySelector(".keterangan-input");

        // Ambil nilai dari textarea
        let cpuValue = cpuInput.value.trim();
        let ramValue = ramInput.value.trim();
        let keteranganValue = keteranganInput.value.trim();

        // Konversi nilai CPU dan RAM yang tersedia ke integer (pastikan bahwa mereka telah diinisialisasi sebelumnya)
        const availableCPU = parseInt(row.querySelector(".available-cpu").textContent.trim(), 10);
        const availableRAM = parseFloat(row.querySelector(".available-ram").textContent.trim());
        // Validasi Reserved CPU
        if (cpuValue !== "" && parseInt(cpuValue, 10) > availableCPU) {
            alert("Reserved CPU tidak boleh melebihi CPU yang tersedia.");
            return; // Berhenti jika validasi gagal
        }

        // Validasi Reserved RAM
        if (ramValue !== "" && parseFloat(ramValue) > availableRAM) {
            alert("Reserved RAM tidak boleh melebihi RAM yang tersedia.");
            return; // Berhenti jika validasi gagal
        }
         // Validasi apakah cpuValue dan ramValue hanya berisi angka
        if (!isValidNumber(cpuValue)) {
            alert("Masukkan hanya angka pada vCPUs.");
            // Lakukan refresh cache (Ctrl+F5)
            location.reload(true);
            return;
        }

        if (!isValidNumber(ramValue)) {
            alert("Masukkan angka saja pada Memory (RAM).");
            // Lakukan refresh cache (Ctrl+F5)
            location.reload(true);
            return;
        }

        console.log(cpuValue);
        console.log(ramValue);
        console.log(keteranganValue);

        // Setel nilai textarea menjadi string kosong jika kosong
        if (cpuValue === null || cpuValue === undefined || cpuValue === "") {
            cpuValue = "";
            cpuInput.value = ""; // Perbarui textarea dengan string kosong
        }
        if (ramValue === null || ramValue === undefined || ramValue === "") {
            ramValue = "";
            ramInput.value = ""; // Perbarui textarea dengan string kosong
        }
        if (keteranganValue === null || keteranganValue === undefined || keteranganValue === "") {
            keteranganValue = "";
            keteranganInput.value = ""; // Perbarui textarea dengan string kosong
        }

        // Buat objek data yang akan disimpan ke dalam JSON
        const dataToSave = {
            [computeName]: {
                CPU: cpuValue,
                RAM: ramValue,
                Kebutuhan: keteranganValue,
            },
        };
        

        // Tambahkan kunci 'CPU', 'RAM', dan 'Kebutuhan' jika kosong
        // if (cpuValue === "") {
        //     dataToSave[computeName].CPU = "";
        // }
        // if (ramValue === "") {
        //     dataToSave[computeName].RAM = "";
        // }
        // if (keteranganValue === "") {
        //     dataToSave[computeName].Kebutuhan = "";
        // }

        console.log(dataToSave)

        // Kirim data ke endpoint di backend untuk disimpan
        fetch("/save_reserved", {
            method: "POST",
            body: JSON.stringify(dataToSave),
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => response.json())
            .then((result) => {
                if (result.success) {
                    alert("Data berhasil disimpan.");
                      // Lakukan refresh cache (Ctrl+F5)
                    location.reload(true);
                } else {
                    alert("Terjadi kesalahan saat menyimpan data.");
                }
            })
            .catch((error) => {
                console.error("Terjadi kesalahan:", error);
                alert("Terjadi kesalahan saat menyimpan data.");
            });
    });
});
