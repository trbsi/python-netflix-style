const form = document.getElementById("magicForm");
const button = document.querySelector(".magic-submit-btn");
const promptInput = document.getElementById("promptInput");
const selectedTagIdsInput = document.getElementById("selectedTagIdsInput");

form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const value = promptInput.dataset.searchText || promptInput.value.trim();
    if (!value) {
        alert('Describe your favorite porn');
        return;
    }

    button.classList.add("loading");
    button.textContent = "Searching...";

    try {
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        await fetch(discoverVideosUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            credentials: "same-origin",
            body: JSON.stringify({
                text: value,
                selected_tag_ids: selectedTagIdsInput ? selectedTagIdsInput.value : "",
            })
        });

        hideVideos();

        setTimeout(() => {
            location.reload();
        }, 2000);

    } catch (err) {
        console.error(err);
    } finally {
        button.classList.remove("loading");
        button.disabled = false;
        button.textContent = "Search";
    }
});

function hideVideos() {
    const sections = document.querySelectorAll(".video-section-content");
    sections.forEach((section, index) => {
        section.style.height = section.offsetHeight + "px";
        section.style.overflow = "hidden";

        section.style.transition = `
            opacity 0.8s ease,
            transform 0.8s ease,
            filter 0.8s ease,
            height 0.8s ease,
            margin 0.8s ease,
            padding 0.8s ease
        `;

        setTimeout(() => {
            section.style.opacity = "0";
            section.style.transform = "translateY(40px) scale(.96)";
            section.style.filter = "blur(12px)";
            section.style.height = "0";
            section.style.margin = "0";
            section.style.paddingTop = "0";
            section.style.paddingBottom = "0";
        }, index * 350);

        setTimeout(() => {
            section.remove();
        }, 1200 + (index * 350));
    });
}
