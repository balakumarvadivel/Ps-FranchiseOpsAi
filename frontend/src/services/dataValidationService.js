import api from "./api";

export const dataValidationService = {
  schemas: () => api.get("/data-validation/schemas").then((r) => r.data),

  upload: (file, datasetType) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("dataset_type", datasetType);
    return api
      .post("/data-validation/upload", formData, { headers: { "Content-Type": "multipart/form-data" } })
      .then((r) => r.data);
  },

  commit: (datasetType, rows) =>
    api.post("/data-validation/commit", { dataset_type: datasetType, rows }).then((r) => r.data),
};
