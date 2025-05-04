// Configure Dropzone
Dropzone.autoDiscover = false;

const myDropzone = new Dropzone("#upload-form", {
  paramName: "file",
  maxFilesize: 100, // MB
  acceptedFiles: ".mp3,.wav,.flac,.ogg,.m4a,.aac",
  timeout: 180000, // 3 minutes
  dictDefaultMessage: "Drop audio files here to split into stems",
  init: function () {
    this.on("success", function (file, response) {
      const statusEl = document.getElementById("status");
      statusEl.textContent =
        "File processed successfully! Check the stems list below.";
      statusEl.className = "status success";

      // Refresh the stems list
      loadStems();

      // Clear the upload after 2 seconds
      setTimeout(() => {
        this.removeFile(file);
      }, 2000);
    });

    this.on("error", function (file, errorMessage) {
      const statusEl = document.getElementById("status");
      statusEl.textContent =
        typeof errorMessage === "string"
          ? errorMessage
          : errorMessage.error || "An error occurred during upload";
      statusEl.className = "status error";
    });

    this.on("sending", function (file) {
      const statusEl = document.getElementById("status");
      statusEl.textContent = "Processing file... This may take a few minutes.";
      statusEl.className = "status";
      statusEl.style.display = "block";
      statusEl.style.backgroundColor = "#fcf8e3";
      statusEl.style.color = "#8a6d3b";
    });
  },
});

// Function to load available stems
function loadStems() {
  fetch("/stems")
    .then((response) => response.json())
    .then((files) => {
      const stemsListEl = document.getElementById("stems-list");

      if (files.length === 0) {
        stemsListEl.innerHTML =
          "<p>No stems available yet. Upload a song to generate stems.</p>";
        return;
      }

      stemsListEl.innerHTML = "";
      files.forEach((file) => {
        const div = document.createElement("div");
        div.className = "stem-item";

        const link = document.createElement("a");
        link.href = `/download/${encodeURIComponent(file)}`;
        link.textContent = file;

        div.appendChild(link);
        stemsListEl.appendChild(div);
      });
    })
    .catch((error) => {
      console.error("Error loading stems:", error);
      document.getElementById("stems-list").innerHTML =
        "<p>Error loading stems. Please refresh the page and try again.</p>";
    });
}

// Load stems on page load
document.addEventListener("DOMContentLoaded", loadStems);
