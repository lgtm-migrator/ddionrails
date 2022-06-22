import "datatables.net-bs4";
import "datatables.net-buttons-bs4";
import "datatables.net-buttons/js/buttons.colVis.js";
import "datatables.net-responsive-bs4";

const questionsApiURL = new URL("api/questions/", window.location.origin);
const urlPart = "question";
const study = document.head.querySelector('meta[name="study"]').content;
const instrument = document.head.querySelector('meta[name="instrument"]').content;

const inputTemplate = document.createElement("input");
inputTemplate.type = "text";
inputTemplate.classList.add("form-control", "form-control-sm");

/**
 * Renders a table of questions.
 *
 * @param {Element} table Empty table to be filled through dataTable instantiation.
 * @param {*} url         API URL to call for the metadata of the desired entities.
 * @return {DataTable}    A dataTable object with full API.
 */
function renderVariableTable(table, url) {
  // eslint-disable-next-line new-cap
  return $(table).DataTable({
    ajax: {
      url,
      dataSrc: "",
      cache: true,
    },
    order: [[2, "asc"]],
    columns: [
      {
        data: "name", // Human readable label.
        orderable: false,
        render(_data, _type, row) {
          const link = document.createElement("a");
          link.href =
            window.location.protocol +
            "//" +
            window.location.hostname +
            `/${urlPart}/${row["id"]}`;
          link.textContent = row["name"];
          return link.outerHTML;
        },
      },
      {
        data: "label", // Human readable label.
        orderable: false,
        render(_data, _type, row) {
          return row["label"] ? row["label"] : row["name"];
        },
      },
      {
        data: "position",
        render(_data, _type, row) {
          return row["position"];
        },
        visible: false,
      },
    ],
  });
}

/**
 *
 * @param {*} table    DOM element object of the table.
 * @param {*} tableAPI dataTable object of the table with full API.
 * @return {object}    Maps column names to input elements.
 */
function addSearchInput(table) {
  const header = table.querySelectorAll(".header > th");
  const searchInputs = {};
  for (const headerColumn of header) {
    const columnName = headerColumn.getAttribute("title");
    const searchHead = table.querySelector(`.search-header > .${columnName}`);
    const searchInput = inputTemplate.cloneNode();
    searchHead.appendChild(searchInput);
    searchInputs[columnName.toString()] = searchInput;
  }
  return searchInputs;
}

/**
 *
 * @param {*} event
 * @param {*} columnName
 * @param {*} tableAPI
 */
function addSearchEvent(event) {
  event.currentTarget.tableAPI
    .column(`.${event.currentTarget.column}`)
    .search(event.currentTarget.value)
    .draw();
}

window.addEventListener("load", function() {
  const questionsTable = document.querySelector("#question-table");

  const questionsAPI = new URL(questionsApiURL.toString());
  questionsAPI.searchParams.append("study", study);
  questionsAPI.searchParams.append("paginate", "False");
  questionsAPI.searchParams.append("instrument", instrument);
  const tableAPI = renderVariableTable(questionsTable, questionsAPI);
  const columnInputMapping = addSearchInput(questionsTable);
  for (const columnName of Object.keys(columnInputMapping)) {
    columnInputMapping[columnName.toString()].column = columnName;
    columnInputMapping[columnName.toString()].tableAPI = tableAPI;
    columnInputMapping[columnName.toString()].addEventListener(
      "input",
      addSearchEvent
    );
  }
});