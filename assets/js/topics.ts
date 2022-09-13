/* !
 * Initialize a fancytree to display topics, concepts and their relation.
 * Also provides frontend functionality to:
 * - Display variables or questions related to a topic/concept.
 * - Add variables related to a topic/concept to a basket.
 * - Switch display language.
 * - Copy a link to share a currently opened topic/concept in the tree.
 *
 *
 * fancytree configuration partly retained from an older script by cstolpe
 *
 * @author hansendx
 */

// Credit to https://github.com/mar10/fancytree/issues/793
import "jquery.fancytree";
import "jquery.fancytree/dist/modules/jquery.fancytree.filter";
import "jquery.fancytree/dist/modules/jquery.fancytree.glyph";
import "datatables.net-bs4";
import "datatables.net-buttons-bs4";
import "datatables.net-buttons/js/buttons.colVis.js";
import "datatables.net-responsive-bs4";
import $ from "jquery";

const context = JSON.parse(document.getElementById("context_data").textContent);
const study = context["study"];

const basketVariableApiUrl = new URL(
  "api/basket-variables/",
  window.location.origin
);
const basketApiUrl = new URL("api/baskets/", window.location.origin);
const variablesApiUrl = new URL("api/variables/", window.location.origin);
const questionsApiUrl = new URL("api/questions/", window.location.origin);
const topicTreeAPI = new URL(`/api/topic-tree/`, window.location.origin);
topicTreeAPI.searchParams.append("study", study);
topicTreeAPI.searchParams.append("language", context["language"]);

interface StringHashMap {
  [details: string]: string;
}

/**
 * Iterate over the attributes of a generic object and add them to an HTML element.
 *
 * @param {Element} element The element to which the attributes should be added.
 * @param {Object} attributes The attributes, that should be added.
 */
function setAttributes(element: HTMLElement, attributes: StringHashMap) {
  for (const [name, value] of Object.entries(attributes)) {
    element.setAttribute(name, value);
  }
}

/**
 * Renders a table of either variables or questions related through a concept or topic.
 *
 * Displays the entities themselves and their immediate parents in the model hierarchy.
 * Entity and parent names are enclosed by a link to their representation on the site.
 *
 * @param {Object} entity Metadata about the type of related entities to render.
 *                        Can be of type variable or question.
 *                        Further contains information about how to retrieve and
 *                        display the entities immediate parent model.
 * @param {Element} table Empty table to be filled through dataTable instantiation.
 * @param {*} url         API URL to call for the metadata of the desired entities.
 */
function renderEntityTable(entity: any, table: string, url: string) {
  $(table).dataTable({
    ajax: {
      url,
      dataSrc: "",
    },
    columns: [
      {
        data: "label", // Human readable label.
        render(_data: any, _type: any, row: StringHashMap) {
          if (window.location.pathname.endsWith("de")) {
            return row["label_de"] ? row["label_de"] : row["name"];
          } else {
            return row["label"] ? row["label"] : row["name"];
          }
        },
      },
      {
        data: "entity", // Actual name of the entity.
        render(_data: any, _type: any, row: StringHashMap) {
          const link = document.createElement("a");
          link.href =
            window.location.protocol +
            "//" +
            window.location.hostname +
            `/${study}/${entity.parentURL}/` +
            row[entity.parentType] +
            "/" +
            row["name"];
          link.textContent = row["name"];

          return link.outerHTML;
        },
      },
      {
        data: "parent",
        render(_data: any, _type: any, row: StringHashMap) {
          const link = document.createElement("a");
          link.href =
            window.location.protocol +
            "//" +
            window.location.hostname +
            `/${study}/${entity.parentURL}/` +
            row[entity.parentType];
          link.textContent = row[entity.parentType];

          return link.outerHTML;
        },
      },
    ],
  });
}

/**
 * Update language switching links to maintain displayed related elements.
 * @param {Object} params key-value pairs to identify currently opened related elements.
 */
function updateLanguageSwitch(params: StringHashMap) {
  for (const id of ["language-switch-de", "language-switch-en"]) {
    const switchLink = document.getElementById(id) as HTMLLinkElement;
    const url = new URL(switchLink.href);
    for (const [key, value] of Object.entries(params)) {
      url.searchParams.set(key, value);
    }
    switchLink.setAttribute("href", url.toString());
  }
}

/**
 * Load and display variable data through a dataTable
 *
 * @param {fancytreeNode} fancytreeNode Topic or concept Node in topic tree
 * @param {HTMLTableElement} relatedVariableSection Target table to fill with the data
 */
function renderVariableTable(
  fancytreeNode: any,
  relatedVariableSection: HTMLElement
) {
  updateLanguageSwitch({
    "related-id": fancytreeNode.key,
    "related-type": "variables",
  });
  const categoryName = fancytreeNode.key.substring(
    fancytreeNode.type.length + 1
  );
  const api = new URL(variablesApiUrl.toString());
  api.searchParams.append("study", study);
  api.searchParams.append(fancytreeNode.type, categoryName);

  const variableTable = document
    .getElementById("variable-table")
    .cloneNode(true) as HTMLElement;
  variableTable.classList.remove("hidden");
  variableTable.id = "used-variable-table";
  relatedVariableSection.appendChild(variableTable);

  const variable = {
    type: "variable",
    parentURL: "data",
    parentType: "dataset_name",
  };
  renderEntityTable(variable, `#${variableTable.id}`, api.toString());
}

/**
 * Load and display question data through a dataTable
 *
 * @param {fancytreeNode} fancytreeNode Topic or concept Node in topic tree
 * @param {HTMLTableElement} relatedQuestionSection Target table to fill with the data
 */
function renderQuestionTable(
  fancytreeNode: any,
  relatedQuestionSection: HTMLElement
) {
  updateLanguageSwitch({
    "related-id": fancytreeNode.key,
    "related-type": "questions",
  });
  const categoryName = fancytreeNode.key.substring(
    fancytreeNode.type.length + 1
  );
  const api = new URL(questionsApiUrl.toString());
  api.searchParams.append("study", study);
  api.searchParams.append(fancytreeNode.type, categoryName);

  const questionTable = document
    .getElementById("question-table")
    .cloneNode(true) as HTMLElement;
  questionTable.classList.remove("hidden");
  questionTable.id = "used-question-table";
  relatedQuestionSection.appendChild(questionTable);
  const question = {
    type: "question",
    parentURL: "inst",
    parentType: "instrument_name",
  };
  renderEntityTable(question, `#${questionTable.id}`, api.toString());
}

/**
 * Retrieve and display related questions or variables for a topic or concept.
 *
 * @param {HTMLButtonElement} node A button Element associated with a topic or concept
 */
function renderRelatedEntities(node: any) {
  // Remove previous table
  const relatedEntitiesTableSection = document.querySelector(
    "#related-elements > div"
  ) as HTMLElement;
  relatedEntitiesTableSection.innerHTML = "";

  const activeNode = $.ui.fancytree.getNode(node);

  if (node.classList.contains("variables")) {
    renderVariableTable(activeNode, relatedEntitiesTableSection);
  } else if (node.classList.contains("questions")) {
    renderQuestionTable(activeNode, relatedEntitiesTableSection);
  }
}

/**
 * Copy the URL of selected topic to clipboard
 *
 * @param {HTMLButtonElement} node - The button node inside the fancytree node
 */
function copyUrlToClipboard(node: any) {
  const activeNode = $.ui.fancytree.getNode(node);

  const url = new URL(window.location.href.split("?")[0]);
  url.searchParams.append("open", activeNode.key);
  navigator.clipboard.writeText(url.toString());
}

/**
 * Call basket variable API to add variables via their topic or concept.
 *
 * There are two ways to add variables here, by topic and by concept.
 * @author Dominique Hansen
 *
 * @param {Node} buttonNode The Basket Button, that was pressed.
 */
function addToBasket(buttonNode: HTMLElement) {
  const successMessage = document.getElementById("basket_success");
  const errorMessage = document.getElementById("basket_error");
  successMessage.classList.add("hidden");
  errorMessage.classList.add("hidden");

  const type = buttonNode.getAttribute("element-type");
  const name = buttonNode.getAttribute("element-name");
  const postData = {
    basket: buttonNode.getAttribute("basket-id"),
    study,
  } as StringHashMap;
  if (type == "topic") {
    postData["topic"] = name;
  } else {
    postData["concept"] = name;
  }

  const client = new XMLHttpRequest();
  client.open("POST", basketVariableApiUrl, true);
  client.setRequestHeader("Content-type", "application/json");

  const csrfToken = document
    .querySelector("[name=csrfmiddlewaretoken]")
    .getAttribute("value");
  client.withCredentials = true;
  client.setRequestHeader("X-CSRFToken", csrfToken);
  client.setRequestHeader("Accept", "application/json");

  client.onreadystatechange = function () {
    if (client.readyState === XMLHttpRequest.DONE) {
      const status = client.status;
      const _response = JSON.parse(client.responseText);
      if (status === 200 || status === 201) {
        successMessage.textContent = _response["detail"];

        successMessage.classList.remove("hidden");
      }
      if (status >= 400) {
        errorMessage.textContent = _response["detail"];
        errorMessage.classList.remove("hidden");
      }
    }
  };
  client.send(JSON.stringify(postData));
}

/**
 * Prompt to add all variables of a topic or concept to a basket.
 * @param {HTMLButtonElement} node A button Element associated with a topic or concept
 */
function renderBasketButtons(node: any) {
  const basketInterfaceModal = document.querySelector(
    "#topic-list-add-to-basket >* .modal-body"
  );
  const fancytreeNode = $.ui.fancytree.getNode(node) as any;
  const categoryType = fancytreeNode.type;
  // The node key will be something like topic_name or concept_name.
  // To retrieve the name we can remove type+"_" from the key.
  const categoryName = fancytreeNode.key.substring(categoryType.length + 1);

  const variableNumberNode = document.getElementById("number-of-variables");
  variableNumberNode.textContent = "";

  const variableApi = new URL(variablesApiUrl.toString());
  variableApi.searchParams.append("study", study);
  variableApi.searchParams.append(categoryType, categoryName);
  variableApi.searchParams.append("paginate", "True");
  variableApi.searchParams.append("limit", "1");

  const variableCountRequest = new XMLHttpRequest();

  variableCountRequest.onreadystatechange = function () {
    if (variableCountRequest.readyState == XMLHttpRequest.DONE) {
      if (variableCountRequest.status == 200) {
        const response = JSON.parse(variableCountRequest.responseText);
        variableNumberNode.textContent = response["count"];
      }
    }
  };
  variableCountRequest.open("GET", variableApi);
  variableCountRequest.send();

  basketInterfaceModal.querySelectorAll(".btn").forEach((btn) => btn.remove());

  const basketListRequest = new XMLHttpRequest();
  const basketApi = new URL(basketApiUrl.toString());
  basketApi.searchParams.append("study", study);

  basketListRequest.onreadystatechange = function () {
    if (basketListRequest.readyState == XMLHttpRequest.DONE) {
      if (basketListRequest.status == 200) {
        const response = JSON.parse(basketListRequest.responseText);

        if (response["count"] == 0) {
          const createBasketLink = document.createElement("a");
          createBasketLink.href = new URL(
            "/workspace/baskets",
            window.location.origin
          ).toString();
          createBasketLink.innerHTML = "Create a basket for this study";
          //basketInterfaceModal.querySelectorAll("*").forEach((n) => n.remove());
          basketInterfaceModal.append(createBasketLink);
          return;
        }

        // Create a button for every Basket from the response.
        for (const basket of response["results"]) {
          const basketButton = document.createElement("button");
          basketButton.classList.add("btn", "btn-primary");
          setAttributes(basketButton, {
            type: "button",
            title: `Add to basket ${basket.name}`,
            "basket-id": basket.id,
            "element-type": categoryType,
            "element-name": categoryName,
          });
          basketButton.textContent = `Add to basket ${basket.name}`;
          basketButton.addEventListener("click", function (event) {
            addToBasket(event.target as HTMLElement);
          });
          basketInterfaceModal.append(basketButton);
        }
      } else if (basketListRequest.status == 403) {
        const loginLink = document.createElement("a");
        loginLink.href = new URL(
          "/workspace/login",
          window.location.origin
        ).toString();
        loginLink.innerHTML = "Please log in to use this function.";
        document.getElementById("basket_list").append(loginLink);
      }
    }
  };
  basketListRequest.open("GET", basketApi);
  basketListRequest.send();
}

// Define what the tree structure will look like, for more information and
// options see https://github.com/mar10/fancytree.
// Build and append tree to #tree.
window.addEventListener("load", () => {
  $("#tree").fancytree({
    extensions: ["filter", "glyph"],
    types: {
      topic: {
        icon: "fas fa-cogs",
      },
      concept: {
        icon: "fas fa-cog",
      },
      variable: {
        icon: "fas fa-chart-bar",
      },
      question: {
        icon: "fas fa-tasks",
      },
    },
    filter: {
      counter: false,
      mode: "hide",
    },
    glyph: {
      preset: "awesome5",
      map: {
        _addClass: "",
        checkbox: "fas fa-square",
        checkboxSelected: "fas fa-check-square",
        checkboxUnknown: "fas fa-square",
        radio: "fas fa-circle",
        radioSelected: "fas fa-circle",
        radioUnknown: "fas fa-dot-circle",
        dragHelper: "fas fa-arrow-right",
        dropMarker: "fas fa-long-arrow-right",
        error: "fas fa-exclamation-triangle",
        expanderClosed: "fas fa-caret-right",
        expanderLazy: "fas fa-angle-right",
        expanderOpen: "fas fa-caret-down",
        loading: "fas fa-spinner fa-pulse",
        nodata: "fas fa-meh",
        noExpander: "",
        /** Default node icons.
         * (Use tree.options.icon callback to define
         * custom icons based on node data)
         */
        doc: "fas fa-file",
        docOpen: "fas fa-file",
        folder: "fas fa-folder",
        folderOpen: "fas fa-folder-open",
      },
    },
    source: {
      url: topicTreeAPI, // load data from api (topic and concepts only)
      cache: true,
    },
    /**
     * Append functional buttons to fancytree nodes.
     * @param {*} _event _
     * @param {*} data Metadata for the node.
     */
    createNode(_event: any, data: any) {
      const filterOptionsString = document.createElement("span");
      filterOptionsString.classList.add(
        "btn-group",
        "btn-group-sm",
        "filter-options"
      );
      setAttributes(filterOptionsString, {
        "data-container": "body",
        role: "group",
      });

      const displayButtons = [document.createElement("button")];
      setAttributes(displayButtons[0], {
        class: "btn btn-link filter-option-variable",
        type: "button",
        "data-tooltip": "tooltip",
        "data-container": "body",
        title: "Show all related variables",
      });

      displayButtons[1] = displayButtons[0].cloneNode() as HTMLButtonElement;
      const basketButton = displayButtons[0].cloneNode() as HTMLButtonElement;

      displayButtons[1].setAttribute("title", "Show all related questions");
      displayButtons[0].innerHTML =
        "<span class='fas fa-chart-bar' aria-hidden='true'></span>";
      displayButtons[0].classList.add("variables");
      displayButtons[1].classList.add("questions");
      displayButtons[1].innerHTML =
        "<span class='fas fa-tasks' aria-hidden='true'></span>";

      setAttributes(basketButton, {
        title: "Add all related variables to one of your baskets",
        "data-toggle": "modal",
        "data-target": "#topic-list-add-to-basket",
      });
      basketButton.innerHTML =
        "<span class='fas fa-shopping-cart' aria-hidden='true'></span>";

      basketButton.addEventListener("click", function (event) {
        renderBasketButtons(event.target);
      });
      for (const button of displayButtons) {
        button.addEventListener("click", (event) => {
          renderRelatedEntities(event.target);
        });
        filterOptionsString.append(button);
      }
      filterOptionsString.append(basketButton);

      if (data.node["type"] === "topic") {
        const clipboard = document.createElement("button");
        clipboard.classList.add("btn", "btn-link");
        setAttributes(clipboard, {
          type: "button",
          "data-tooltip": "tooltip",
          "data-container": "body",
          title: "Copy URL",
        });
        clipboard.innerHTML =
          "<span class='fas fa-copy' aria-hidden='true'></span>";
        clipboard.addEventListener("click", function (event) {
          copyUrlToClipboard(event.target);
        });
        filterOptionsString.append(clipboard);
      }

      data.node.span
        .querySelector(".fancytree-title")
        .insertAdjacentElement("afterend", filterOptionsString);
    },
    /**
     * Open specific fancytree node that is specified in a searchParam
     */
    init() {
      const toOpen = new URL(window.location.href).searchParams.get("open");

      if (toOpen != null) {
        const node = $.ui.fancytree.getTree("#tree").getNodeByKey(toOpen);
        node.makeVisible();
        node.setActive(true);
      }
      const categoryID = new URL(window.location.href).searchParams.get(
        "related-id"
      );
      const relatedType = new URL(window.location.href).searchParams.get(
        "related-type"
      );
      if (categoryID != null) {
        const relatedEntitiesTableSection = document.querySelector(
          "#related-elements > div"
        ) as HTMLElement;
        const categoryNode = $.ui.fancytree
          .getTree("#tree")
          .getNodeByKey(categoryID);
        if (relatedType === "variables") {
          renderVariableTable(categoryNode, relatedEntitiesTableSection);
        } else if (relatedType === "questions") {
          renderQuestionTable(categoryNode, relatedEntitiesTableSection);
        }
      }
    },
  });

  // Search the tree for search string
  document
    .querySelector("#btn-search")
    .addEventListener("click", (_event: any) => {
      const searchField = document.getElementById("search") as HTMLInputElement;
      const tree = $.ui.fancytree.getTree("#tree") as Fancytree.Fancytree;
      tree.filterBranches(searchField.value);
    });

  // Trigger search on enter
  document
    .querySelector("#search")
    .addEventListener("keyup", (event: KeyboardEvent) => {
      if (event.key === "Enter") {
        (document.querySelector("#btn-search") as HTMLButtonElement).click();
      }
    });
});

/**
 * When basket modal is closed, hide old alert messages.
 * A closed modal can be identified by the lack of a `show`.
 * This is why we check for changes in the class list.
 */
const modalObserver = new MutationObserver(function (mutations) {
  mutations.forEach(function (mutation) {
    if (mutation.attributeName === "class") {
      if (!(mutation.target as HTMLElement).classList.contains("show")) {
        (mutation.target as HTMLElement)
          .querySelectorAll(".modal-body > .alert")
          .forEach(function (node) {
            node.classList.add("hidden");
          });
      }
    }
  });
});

modalObserver.observe(document.getElementById("topic-list-add-to-basket"), {
  attributes: true,
});
