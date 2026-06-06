const form = document.getElementById("magicForm");
const button = document.querySelector(".magic-submit-btn");
const promptInput = document.getElementById("promptInput");

form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const value = promptInput.value;
    if (!value) {
        alert('Describe your favorite porn');
        return;
    }

    button.classList.add("loading");
    button.innerHTML = '<i class="fa-solid fa-spinner"></i>';

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
        button.innerHTML = `<i class="fa-regular fa-circle-right"></i>`;
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
