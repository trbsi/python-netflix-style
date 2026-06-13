function initTagSuggestions({form, promptInput, selectedTagIdsInput, selectedTagsList, suggestionsBox, searchTagsUrl}) {
    const selectedTags = [];
    const tagInputs = Array.from(form.querySelectorAll(".magic-tag-input"));
    const tokenLists = Array.from(form.querySelectorAll("[data-token-list]")).reduce((lists, element) => {
        lists[element.dataset.tokenList] = element;
        return lists;
    }, {});
    let visibleSuggestions = [];
    let searchDebounceTimer = null;
    let searchAbortController = null;
    let activeInput = tagInputs[0] || promptInput;

    syncFormValues();

    tagInputs.forEach((input) => {
        input.addEventListener("focus", function () {
            activeInput = input;
            if (!suggestionsBox.classList.contains("d-none")) {
                positionSuggestionsBox();
            }
        });

        input.addEventListener("input", function () {
            activeInput = input;
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

        input.addEventListener("keydown", function (event) {
            activeInput = input;

            if (event.key === "Tab" && visibleSuggestions.length) {
                event.preventDefault();
                selectTag(visibleSuggestions[0]);
                return;
            }

            if (event.key === "Backspace" && !input.value) {
                const group = getInputGroup(input);
                let lastTagIndex = -1;

                for (let index = selectedTags.length - 1; index >= 0; index--) {
                    if (selectedTags[index].group === group) {
                        lastTagIndex = index;
                        break;
                    }
                }

                if (lastTagIndex !== -1) {
                    selectedTags.splice(lastTagIndex, 1);
                    renderSelectedTags();
                    syncFormValues();
                    clearSuggestions();
                }
            }
        });
    });

    form.addEventListener("click", function (event) {
        if (event.target.closest(".magic-tag-suggestion")) {
            return;
        }

        const panel = event.target.closest("[data-tag-group]");
        if (panel) {
            const input = panel.querySelector(".magic-tag-input");
            if (input) {
                activeInput = input;
                input.focus();
            }
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
                    tag: query,
                    tag_groups: getInputTagGroups(activeInput)
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
            const group = getInputGroup(activeInput);
            return !selectedTags.some((selectedTag) => {
                return selectedTag.group === group && String(selectedTag.id) === String(tag.id);
            });
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
            option.textContent = tag.name;
            option.addEventListener("click", function () {
                selectTag(tag);
            });
            suggestionsBox.appendChild(option);
        });

        const hint = document.createElement("div");
        hint.className = "magic-tag-suggestion-hint";
        hint.textContent = "Press Tab to choose the first tag";
        suggestionsBox.appendChild(hint);

        positionSuggestionsBox();
        suggestionsBox.classList.remove("d-none");
    }

    function selectTag(tag) {
        const group = getInputGroup(activeInput);
        selectedTags.push({
            ...tag,
            group
        });
        activeInput.value = "";
        renderSelectedTags();
        syncFormValues();
        activeInput.focus();
        clearSuggestions();
    }

    function renderSelectedTags() {
        Object.values(tokenLists).forEach((list) => {
            list.innerHTML = "";
        });

        selectedTags.forEach((tag, index) => {
            const list = tokenLists[tag.group] || selectedTagsList;
            const tagElement = document.createElement("span");
            tagElement.className = "magic-selected-tag";

            const text = document.createElement("span");
            text.className = "magic-selected-tag-text";
            text.textContent = tag.name;

            tagElement.appendChild(text);
            list.appendChild(tagElement);
        });
    }

    function syncFormValues() {
        selectedTagIdsInput.value = selectedTags.map((selectedTag) => selectedTag.id).join(",");
        promptInput.dataset.searchText = [
            ...selectedTags.map((selectedTag) => selectedTag.name),
            ...tagInputs.map((input) => input.value.trim())
        ].filter(Boolean).join(", ");
    }

    function getCurrentTagQuery() {
        return activeInput.value.trim();
    }

    function getInputGroup(input) {
        return input.dataset.tagGroup || "active";
    }

    function getInputTagGroups(input) {
        if (getInputGroup(input) === "act") {
            return ["act", "position"];
        }

        return ["role", "appearance"];
    }

    function positionSuggestionsBox() {
        if (!activeInput) {
            return;
        }

        const wrapper = form.querySelector(".magic-input-wrapper");
        const inputRect = activeInput.getBoundingClientRect();
        const wrapperRect = wrapper.getBoundingClientRect();
        const minWidth = 220;
        const maxWidth = wrapper.clientWidth - 24;
        const width = Math.min(Math.max(inputRect.width, minWidth), maxWidth);
        const left = Math.min(
            Math.max(inputRect.left - wrapperRect.left, 12),
            Math.max(wrapper.clientWidth - width - 12, 12)
        );

        suggestionsBox.style.top = `${inputRect.bottom - wrapperRect.top + 8}px`;
        suggestionsBox.style.left = `${left}px`;
        suggestionsBox.style.width = `${width}px`;
    }

    function clearSuggestions() {
        visibleSuggestions = [];
        suggestionsBox.innerHTML = "";
        suggestionsBox.classList.add("d-none");
    }
}
