/**
 * Generate STL from the anything endpoint
 * @param {FormData} formData - FormData with model file and parameters
 * @returns {Promise<{blob: Blob, filename: string}>}
 */
export async function generateFusedSTL(formData) {
  const response = await fetch('/api/anything', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.text().catch(() => 'Model generation failed');
    throw new Error(error || 'Model generation failed');
  }

  // Extract filename from Content-Disposition header
  const contentDisposition = response.headers.get('Content-Disposition');
  let filename = 'anything-goews.stl';
  if (contentDisposition) {
    const match = contentDisposition.match(/filename="?(.+?)"?$/);
    if (match) {
      filename = match[1];
    }
  }

  const blob = await response.blob();
  return { blob, filename };
}

/**
 * Download STL blob as file
 * @param {Blob} blob - STL blob
 * @param {string} filename - Filename for download
 */
export function downloadSTL(blob, filename) {
  const url = URL.createObjectURL(blob);
  try {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } finally {
    URL.revokeObjectURL(url);
  }
}

/**
 * Load STL file as ArrayBuffer
 * @param {File} file - STL file
 * @returns {Promise<ArrayBuffer>}
 */
export function loadSTL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
}
