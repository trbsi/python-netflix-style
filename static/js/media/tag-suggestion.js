function initTagSuggestions({form, promptInput, selectedTagIdsInput, selectedTagsList, suggestionsBox, searchTagsUrl}) {
    const selectedTags = [];
    let visibleSuggestions = [];
    let searchDebounceTimer = null;
    let searchAbortController = null;

    syncFormValues();

    promptInput.addEventListener("input", function () {
        window.clearTimeout(searchDebounceTimer);

        const query = getCurrentTagQuery();
        syncFormValues();

        if (query.length < 3) {
            clearSuggestions();
            return;
        }

        searchDebounceTimer = window.setTimeout(() => {
            searchTags(query);
        }, 250);
    });

    promptInput.addEventListener("keydown", function (event) {
        if (event.key === "Tab" && visibleSuggestions.length) {
            event.preventDefault();
            selectTag(visibleSuggestions[0]);
            return;
        }

        if (event.key === "Backspace" && !promptInput.value && selectedTags.length) {
            selectedTags.pop();
            renderSelectedTags();
            syncFormValues();
            clearSuggestions();
        }
    });

    form.addEventListener("click", function (event) {
        if (!event.target.closest(".magic-tag-suggestion")) {
            promptInput.focus();
        }
    });

    document.addEventListener("click", function (event) {
        if (!form.contains(event.target)) {
            clearSuggestions();
        }
    });

    async function searchTags(query) {
        if (searchAbortController) {
            searchAbortController.abort();
        }

        searchAbortController = new AbortController();

        try {
            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
            const response = await fetch(searchTagsUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                credentials: "same-origin",
                signal: searchAbortController.signal,
                body: JSON.stringify({
                    tag: query
                })
            });

            if (!response.ok) {
                clearSuggestions();
                return;
            }

            const data = await response.json();
            renderSuggestions(data.tags || []);
        } catch (err) {
            if (err.name !== "AbortError") {
                console.error(err);
                clearSuggestions();
            }
        }
    }

    function renderSuggestions(tags) {
        suggestionsBox.innerHTML = "";

        const availableTags = tags.filter((tag) => {
            return !selectedTags.some((selectedTag) => String(selectedTag.id) === String(tag.id));
        });
        visibleSuggestions = availableTags;

        if (!availableTags.length) {
            clearSuggestions();
            return;
        }

        availableTags.forEach((tag) => {
            const option = document.createElement("button");
            option.type = "button";
            option.className = "magic-tag-suggestion";
            option.setAttribute("role", "option");
            option.textContent = tag.raw_tag;
            option.addEventListener("click", function () {
                selectTag(tag);
            });
            suggestionsBox.appendChild(option);
        });

        const hint = document.createElement("div");
        hint.className = "magic-tag-suggestion-hint";
        hint.textContent = "Press Tab to choose the first tag";
        suggestionsBox.appendChild(hint);

        suggestionsBox.classList.remove("d-none");
    }

    function selectTag(tag) {
        selectedTags.push(tag);
        promptInput.value = "";
        renderSelectedTags();
        syncFormValues();
        promptInput.focus();
        clearSuggestions();
    }

    function renderSelectedTags() {
        selectedTagsList.innerHTML = "";

        selectedTags.forEach((tag, index) => {
            const tagElement = document.createElement("span");
            tagElement.className = "magic-selected-tag";

            const text = document.createElement("span");
            text.className = "magic-selected-tag-text";
            text.textContent = tag.raw_tag;

            // const removeButton = document.createElement("button");
            // removeButton.type = "button";
            // removeButton.className = "magic-selected-tag-remove";
            // removeButton.setAttribute("aria-label", `Remove ${tag.raw_tag}`);
            // removeButton.innerHTML = "&times;";
            // removeButton.addEventListener("click", function () {
            //     selectedTags.splice(index, 1);
            //     renderSelectedTags();
            //     syncFormValues();
            //     promptInput.focus();
            // });

            tagElement.appendChild(text);
            // tagElement.appendChild(removeButton);
            selectedTagsList.appendChild(tagElement);
        });
    }

    function syncFormValues() {
        selectedTagIdsInput.value = selectedTags.map((selectedTag) => selectedTag.id).join(",");
        promptInput.dataset.searchText = [
            ...selectedTags.map((selectedTag) => selectedTag.raw_tag),
            promptInput.value.trim()
        ].filter(Boolean).join(", ");
    }

    function getCurrentTagQuery() {
        return promptInput.value.trim();
    }

    function clearSuggestions() {
        visibleSuggestions = [];
        suggestionsBox.innerHTML = "";
        suggestionsBox.classList.add("d-none");
    }
}
