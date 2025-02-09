import "datatables.net-bs4";
import "datatables.net-buttons-bs4";
import "datatables.net-buttons/js/buttons.colVis.js";
import "datatables.net-responsive-bs4";
import * as $ from "jquery";
import initSearchEventHandler from "./search_input_handling";

const instrumentApiURL = new URL("api/instruments/", window.location.origin);
const urlPart = "inst";
const study = document.querySelector("#study-name").getAttribute("value");
const hasExtendedMetadata = document
  .querySelector("#study-name")
  .getAttribute("has-extended-metadata");

const inputTemplate = document.createElement("input");
inputTemplate.type = "text";
inputTemplate.classList.add("form-control", "form-control-sm");

const attachmentIcon = document.createElement("i");
attachmentIcon.classList.add("fa-solid", "fa-file-lines");
const attachmentLinkTemplate = document.createElement("a");
attachmentLinkTemplate.appendChild(attachmentIcon);

/**
 * Renders a table of instruments.
 *
 * @param {Element} table Empty table to be filled through dataTable instantiation.
 * @param {*} url         API URL to call for the metadata of the desired entities.
 * @return {DataTable}    A dataTable object with full API.
 */
function renderFullInstrumentTable(table: any, url: string) {
  // eslint-disable-next-line new-cap
  return $(table).DataTable({
    language: {
      searchPlaceholder: "Search all columns",
    },
    ajax: {
      url,
      dataSrc: "",
      cache: true,
    },
    order: [
      [2, "desc"],
      [3, "asc"],
      [5, "asc"],
    ],
    columns: [
      {
        data: "instrument", // Human readable label.
        render(_data: any, _type: any, row: any) {
          if (row["has_questions"] === true) {
            const link = document.createElement("a");
            link.href =
              window.location.protocol +
              "//" +
              window.location.hostname +
              `/${row["study_name"]}/${urlPart}/${row["name"]}`;
            link.textContent = row["name"];
            return link.outerHTML;
          }
          return row["name"];
        },
      },
      {
        data: "label",
        render(_data: any, _type: any, row: any) {
          return row["label"] ? row["label"] : row["name"];
        },
      },
      {
        data: "period",
        render(_data: any, _type: any, row: any) {
          if (row["period_label"] !== "") {
            return row["period_label"];
          }
          return row["period_name"];
        },
      },
      {
        data: "type_position",
        render(_data: any, _type: any, row: any) {
          return row["type"]["position"];
        },
        visible: false,
      },
      {
        data: "type",
        render(_data: any, _type: any, row: any) {
          return row["type"]["en"];
        },
      },
      {
        data: "mode",
        render(_data: any, _type: any, row: any) {
          return row["mode"];
        },
      },
      {
        data: "attachments",
        className: "attachment",
        orderable: false,
        render(_data: any, _type: any, row: any) {
          const linkContainer = document.createElement("div");
          for (const attachment of row["attachments"]) {
            const link = attachmentLinkTemplate.cloneNode(
              true
            ) as HTMLLinkElement;
            link.href = attachment["url"];
            link.title = attachment["url_text"];
            linkContainer.appendChild(link);
            const text = document.createElement("text");
            text.classList.add("hidden");
            text.textContent = attachment["url_text"];
            linkContainer.appendChild(text);
          }
          return linkContainer.outerHTML;
        },
      },
    ],
  });
}

/**
 * Renders a table of instruments.
 *
 * @param {Element} table Empty table to be filled through dataTable instantiation.
 * @param {*} url         API URL to call for the metadata of the desired entities.
 * @return {DataTable}    A dataTable object with full API.
 */
function renderInstrumentTable(table: any, url: string) {
  // eslint-disable-next-line new-cap
  return $(table).DataTable({
    language: {
      searchPlaceholder: "Search all columns",
    },
    ajax: {
      url,
      dataSrc: "",
      cache: true,
    },
    order: [[2, "desc"]],
    columns: [
      {
        data: "instrument",
        render(_data: any, _type: any, row: any) {
          if (row["has_questions"] === true) {
            const link = document.createElement("a");
            link.href =
              window.location.protocol +
              "//" +
              window.location.hostname +
              `/${row["study_name"]}/${urlPart}/${row["name"]}`;
            link.textContent = row["name"];
            return link.outerHTML;
          }
          return row["name"];
        },
      },
      {
        data: "label",
        render(_data: any, _type: any, row: any) {
          return row["label"] ? row["label"] : row["name"];
        },
      },
      {
        data: "period",
        render(_data: any, _type: any, row: any) {
          return row["period_name"];
        },
      },
      {
        data: "analysis_unit",
        render(_data: any, _type: any, row: any) {
          return row["analysis_unit_name"];
        },
      },
      {
        data: "attachments",
        className: "attachment",
        orderable: false,
        render(_data: any, _type: any, row: any) {
          const linkContainer = document.createElement("div");
          for (const attachment of row["attachments"]) {
            const link = attachmentLinkTemplate.cloneNode(
              true
            ) as HTMLLinkElement;
            link.href = attachment["url"];
            link.title = attachment["url_text"];
            linkContainer.appendChild(link);
            const text = document.createElement("text");
            text.classList.add("hidden");
            text.textContent = attachment["url_text"];
            linkContainer.appendChild(text);
          }
          return linkContainer.outerHTML;
        },
      },
    ],
  });
}

window.addEventListener("load", () => {
  let instrumentTableRenderer: any = null;
  if (hasExtendedMetadata === "True") {
    instrumentTableRenderer = renderFullInstrumentTable;
  } else {
    instrumentTableRenderer = renderInstrumentTable;
  }
  initSearchEventHandler(
    instrumentApiURL,
    study,
    instrumentTableRenderer,
    "#instrument-table"
  );
});
