function initTagSuggestions({ form, promptInput, selectedTagIdsInput, suggestionsBox, searchTagsUrl }) {
    const selectedTags = [];
    let searchDebounceTimer = null;
    let searchAbortController = null;

    promptInput.addEventListener("input", function () {
        window.clearTimeout(searchDebounceTimer);
        syncSelectedTagsFromInput();

        const query = getCurrentTagQuery();
        if (query.length < 3) {
            clearSuggestions();
            return;
        }

        searchDebounceTimer = window.setTimeout(() => {
            searchTags(query);
        }, 250);
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

        suggestionsBox.classList.remove("d-none");
    }

    function selectTag(tag) {
        selectedTags.push(tag);
        selectedTagIdsInput.value = selectedTags.map((selectedTag) => selectedTag.id).join(",");
        promptInput.value = selectedTags.map((selectedTag) => selectedTag.raw_tag).join(", ");
        promptInput.focus();
        clearSuggestions();
    }

    function syncSelectedTagsFromInput() {
        const visibleTags = promptInput.value
            .split(",")
            .map((tag) => tag.trim())
            .filter(Boolean);
        const visibleTagSet = new Set(visibleTags);

        for (let index = selectedTags.length - 1; index >= 0; index--) {
            if (!visibleTagSet.has(selectedTags[index].raw_tag)) {
                selectedTags.splice(index, 1);
            }
        }

        selectedTagIdsInput.value = selectedTags.map((selectedTag) => selectedTag.id).join(",");
    }

    function getCurrentTagQuery() {
        const parts = promptInput.value.split(",");
        return parts[parts.length - 1].trim();
    }

    function clearSuggestions() {
        suggestionsBox.innerHTML = "";
        suggestionsBox.classList.add("d-none");
    }
}
