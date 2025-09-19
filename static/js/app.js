// Extracted app logic from templates/index.html
document.addEventListener("DOMContentLoaded", () => {
  const postForm = document.getElementById("post-form");
  const selectedPlatformEl = document.getElementById("selected-platform");
  const statusEl = document.getElementById("status");

  const STATUS_URL = window.SOCMED_CONFIG?.STATUS_URL || "/api/status";

  function switchPlatform(platform) {
    selectedPlatformEl.value = platform;
    document.querySelectorAll(".tab").forEach((tab) => {
      if (tab.dataset.platform === platform) {
        tab.classList.add("bg-blue-500", "text-white");
        tab.classList.remove("bg-gray-50", "hover:bg-gray-100");
      } else {
        tab.classList.remove("bg-blue-500", "text-white");
        tab.classList.add("bg-gray-50", "hover:bg-gray-100");
      }
    });

    const icon = document.getElementById("submit-icon");
    const text = document.getElementById("submit-text");
    const limit = document.getElementById("char-limit");
    const textarea = document.getElementById("message");
    const fileInput = document.getElementById("media_file");
    const mediaLimits = document.getElementById("media-limits");

    if (platform === "facebook") {
      icon.textContent = "📘";
      text.textContent = "Post to Facebook";
      limit.textContent = "63,206";
      textarea.maxLength = 63206;
      fileInput.multiple = true;
      fileInput.accept = "image/*,video/*";
      mediaLimits.textContent = "Up to 10 images or 1 video per post";
    } else if (platform === "twitter") {
      icon.textContent = "🐦";
      text.textContent = "Post to Twitter";
      limit.textContent = "280";
      textarea.maxLength = 280;
      fileInput.multiple = true;
      fileInput.accept = "image/*,video/*";
      mediaLimits.textContent = "Up to 4 images/videos per tweet";
    } else if (platform === "instagram") {
      icon.textContent = "📸";
      text.textContent = "Post to Instagram";
      limit.textContent = "2,200";
      textarea.maxLength = 2200;
      fileInput.multiple = true;
      fileInput.accept = "image/*";
      mediaLimits.textContent = "Up to 10 images per carousel (images only)";
    }
    updateCharCount();
    checkStatus();
  }

  function updateCharCount() {
    const textarea = document.getElementById("message");
    const counter = document.getElementById("char-count");
    const length = textarea.value.length;
    counter.textContent = length;

    const platform = selectedPlatformEl.value;
    if (platform === "twitter") {
      counter.className =
        length > 280
          ? "text-red-500"
          : length > 250
          ? "text-yellow-500"
          : "text-gray-500";
    } else {
      counter.className = "text-gray-500";
    }
  }

  function previewFile() {
    const fileInput = document.getElementById("media_file");
    const files = fileInput.files;
    const preview = document.getElementById("media-preview");
    const platform = selectedPlatformEl.value;
    document.getElementById("image_url").value = "";

    if (!files || files.length === 0) {
      preview.innerHTML = "";
      return;
    }

    if (files.length > 1) {
      preview.innerHTML = "";
      let maxFiles = platform === "twitter" ? 4 : 10;
      let errorMessage =
        platform === "twitter"
          ? "Twitter allows maximum 4 media files per tweet."
          : "Maximum 10 files allowed for this platform.";
      if (files.length > maxFiles) {
        preview.innerHTML = `<div class="p-3 bg-red-100 text-red-700 rounded-md">${errorMessage}</div>`;
        return;
      }

      preview.innerHTML = `<div class="mb-2 text-sm text-gray-600">📎 ${files.length} files selected for ${platform}:</div>`;
      const gridDiv = document.createElement("div");
      gridDiv.className = "grid grid-cols-2 sm:grid-cols-3 gap-2 mt-2";
      Array.from(files).forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const itemDiv = document.createElement("div");
          itemDiv.className =
            "relative border border-gray-300 rounded overflow-hidden";
          if (file.type.startsWith("image/")) {
            itemDiv.innerHTML = `\n              <img src="${
              e.target.result
            }" alt="Preview ${
              index + 1
            }" class="w-full h-20 object-cover">\n              <div class="absolute top-1 right-1 bg-black bg-opacity-75 text-white text-xs px-1 rounded">${
              index + 1
            }</div>`;
          } else {
            itemDiv.innerHTML = `\n              <video class="w-full h-20 object-cover" muted>\n                <source src="${
              e.target.result
            }" type="${
              file.type
            }">\n              </video>\n              <div class="absolute top-1 right-1 bg-black bg-opacity-75 text-white text-xs px-1 rounded">🎥 ${
              index + 1
            }</div>`;
          }
          gridDiv.appendChild(itemDiv);
        };
        reader.readAsDataURL(file);
      });
      preview.appendChild(gridDiv);
    } else {
      const file = files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        if (file.type.startsWith("image/")) {
          preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        } else {
          preview.innerHTML = `<video controls><source src="${e.target.result}" type="${file.type}"></video>`;
        }
      };
      reader.readAsDataURL(file);
    }
  }

  function previewFromUrl() {
    const url = document.getElementById("image_url").value.trim();
    const preview = document.getElementById("media-preview");
    if (document.getElementById("media_file").files.length > 0) return;
    preview.innerHTML = url ? `<img src="${url}" alt="Preview">` : "";
  }

  async function checkStatus() {
    statusEl.textContent = "Checking connection...";
    statusEl.className =
      "p-3 rounded-md text-sm mt-5 bg-yellow-100 text-yellow-800 border border-yellow-200";
    try {
      const platform = selectedPlatformEl.value;
      const url = `${STATUS_URL}?platform=${platform}`;
      const res = await fetch(url);
      const data = await res.json();
      const ok =
        (platform === "facebook" &&
          data.facebook?.token_valid &&
          data.facebook?.page_access) ||
        (platform === "twitter" && data.twitter?.credentials_valid) ||
        (platform === "instagram" &&
          data.instagram?.token_valid &&
          data.instagram?.account_access);

      statusEl.textContent = ok
        ? `✓ Connected to ${platform}`
        : `✗ Connection failed`;
      statusEl.className = ok
        ? "p-3 rounded-md text-sm mt-5 bg-green-100 text-green-800 border border-green-200"
        : "p-3 rounded-md text-sm mt-5 bg-red-100 text-red-800 border border-red-200";
    } catch (e) {
      statusEl.textContent = "✗ Unable to check status";
      statusEl.className =
        "p-3 rounded-md text-sm mt-5 bg-red-100 text-red-800 border border-red-200";
    }
  }

  function resetForm() {
    postForm.reset();
    document.getElementById("media-preview").innerHTML = "";
    updateCharCount();
  }

  // Expose functions to inline handlers (onchange/onclick) used in template
  window.switchPlatform = switchPlatform;
  window.previewFile = previewFile;
  window.previewFromUrl = previewFromUrl;
  window.updateCharCount = updateCharCount;
  window.resetForm = resetForm;
  window.checkStatus = checkStatus;

  // Initialize from inline config
  const initialPlatform = window.SOCMED_CONFIG?.INITIAL_PLATFORM || "facebook";
  switchPlatform(initialPlatform);
  checkStatus();
  updateCharCount();

  // Auto-hide flash messages after 3 seconds
  const flashMessage = document.getElementById("flash-message");
  if (flashMessage) {
    setTimeout(() => {
      flashMessage.style.opacity = "0";
      setTimeout(() => (flashMessage.style.display = "none"), 500);
    }, 3000);
  }
});
