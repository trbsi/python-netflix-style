(function () {
    "use strict";

    const cards = Array.from(document.querySelectorAll(".single-video-card"));
    const rowPanel = document.querySelector("[data-video-expanded-row]");
    const embed = rowPanel && rowPanel.querySelector("[data-video-embed]");
    const closeButton = rowPanel && rowPanel.querySelector(".single-video-close");
    let activeCard = null;

    if (!cards.length || !rowPanel || !embed) {
        return;
    }

    function getTrigger(card) {
        return card.querySelector("[data-video-trigger]");
    }

    function getTemplate(card) {
        return card.querySelector("[data-video-embed-template]");
    }

    function resetTriggers() {
        cards.forEach((card) => {
            const trigger = getTrigger(card);

            if (!trigger) {
                return;
            }

            trigger.classList.remove("is-expanded");
            trigger.setAttribute("aria-expanded", "false");
        });
    }

    function closePanel() {
        resetTriggers();
        rowPanel.classList.add("d-none");
        embed.innerHTML = "";
        activeCard = null;
    }

    function getLastCardInVisualRow(card) {
        const rowTop = card.offsetTop;
        let lastCard = card;

        cards.forEach((item) => {
            if (Math.abs(item.offsetTop - rowTop) > 2) {
                return;
            }

            if (item.offsetLeft >= lastCard.offsetLeft) {
                lastCard = item;
            }
        });

        return lastCard;
    }

    function placePanel(card) {
        const lastCard = getLastCardInVisualRow(card);
        lastCard.insertAdjacentElement("afterend", rowPanel);
    }

    function scrollToPanel() {
        const headerOffset = 90;
        const panelTop = rowPanel.getBoundingClientRect().top + window.scrollY - headerOffset;

        window.scrollTo({
            top: Math.max(panelTop, 0),
            behavior: "auto"
        });
    }

    function openPanel(card) {
        const trigger = getTrigger(card);
        const template = getTemplate(card);

        if (!trigger || !template) {
            return;
        }

        resetTriggers();
        placePanel(card);
        embed.innerHTML = template.innerHTML.trim();
        rowPanel.classList.remove("d-none");
        trigger.classList.add("is-expanded");
        trigger.setAttribute("aria-expanded", "true");
        activeCard = card;
        scrollToPanel();
    }

    function togglePanel(card) {
        if (activeCard === card && !rowPanel.classList.contains("d-none")) {
            closePanel();
            return;
        }

        openPanel(card);
    }

    cards.forEach((card) => {
        const trigger = getTrigger(card);

        if (!trigger) {
            return;
        }

        trigger.addEventListener("click", () => togglePanel(card));

        trigger.addEventListener("keydown", (event) => {
            if (event.key !== "Enter" && event.key !== " ") {
                return;
            }

            event.preventDefault();
            togglePanel(card);
        });
    });

    if (closeButton) {
        closeButton.addEventListener("click", () => {
            const trigger = activeCard && getTrigger(activeCard);

            closePanel();

            if (trigger) {
                trigger.focus();
            }
        });
    }

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") {
            return;
        }

        closePanel();
    });

    window.addEventListener("resize", () => {
        if (!activeCard || rowPanel.classList.contains("d-none")) {
            return;
        }

        placePanel(activeCard);
    });
}());
