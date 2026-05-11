<script>
  import { loadSTL } from '../lib/api.js';

  let { fileName = '', fileload = () => {}, remove = () => {}, onerror = () => {} } = $props();
  
  let isDragging = $state(false);
  let isLoading = $state(false);
  let loaded = $state(false);

  async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
      await loadFile(file);
    }
  }

  async function handleDrop(event) {
    event.preventDefault();
    isDragging = false;
    
    const file = event.dataTransfer.files[0];
    if (file && file.name.toLowerCase().endsWith('.stl')) {
      await loadFile(file);
    }
  }

  function handleDragOver(event) {
    event.preventDefault();
    isDragging = true;
  }

  function handleDragLeave() {
    isDragging = false;
  }

  async function loadFile(file) {
    if (!file.name.toLowerCase().endsWith('.stl')) {
      onerror('Please upload an STL file');
      return;
    }

    if (file.size > 100 * 1024 * 1024) {
      onerror('File too large (max 100MB)');
      return;
    }

    isLoading = true;

    try {
      const arrayBuffer = await loadSTL(file);
      loaded = true;
      fileload({ file, data: arrayBuffer });
    } catch (e) {
      onerror('Error loading file: ' + e.message);
    } finally {
      isLoading = false;
    }
  }

  function handleRemove() {
    loaded = false;
    remove();
  }
</script>

<div
  role="button"
  tabindex="0"
  class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center transition-colors cursor-pointer relative
    {isDragging ? 'border-blue-500 bg-blue-50 border-solid' : 'hover:border-blue-500 hover:bg-blue-50'}
    {loaded ? 'border-green-500 bg-green-50 border-solid' : 'bg-gray-50'}"
  ondragover={handleDragOver}
  ondragleave={handleDragLeave}
  ondrop={handleDrop}
>
  {#if isLoading}
    <div class="flex flex-col items-center gap-3">
      <svg class="w-10 h-10 animate-spin text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
      <p class="text-gray-500">Loading...</p>
    </div>
  {:else if loaded}
    <div class="flex flex-col items-center gap-3">
      <svg class="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-sm text-green-700 font-medium break-all">{fileName || 'STL file loaded'}</p>
      <button class="flex items-center gap-1 py-1 px-3 bg-white border border-gray-300 rounded text-sm text-gray-600 hover:bg-gray-50"
        onclick={(e) => { e.preventDefault(); handleRemove(); }}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
        Change file
      </button>
    </div>
    <input type="file" accept=".stl" id="file-input" onchange={handleFileSelect}
      class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
  {:else}
    <input type="file" accept=".stl" id="file-input" onchange={handleFileSelect}
      class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
    <label for="file-input" class="flex flex-col items-center gap-2 cursor-pointer">
      <svg class="w-12 h-12 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
      <p class="text-gray-700"><strong>Click to upload</strong> or drag and drop</p>
      <p class="text-sm text-gray-500">STL files only (max 100MB)</p>
    </label>
  {/if}
</div>
