async function sendFile() {
    const fileInput = document.getElementById("fileInput");
    const result = document.getElementById("result");

    if (!fileInput.files.length) {
        alert("Seleccione un archivo");
        return;
    }

    result.value = "Generando resumen, por favor espere...";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch("/summarize", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    if (data.summary) {
        result.value = data.summary;
    } else {
        result.value = "Error: " + data.error;
    }
}
