<script>
  import { onMount } from 'svelte';
  import STLViewer from './components/STLViewer.svelte';
  import STLUpload from './components/STLUpload.svelte';
  import PlateConfig from './components/PlateConfig.svelte';
  import TransformControls from './components/TransformControls.svelte';
  import { generateFusedSTL, downloadSTL } from './lib/api.js';

  const STORAGE_KEY = 'anything-goews-state';

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) return JSON.parse(raw);
    } catch {}
    return null;
  }

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        plateUnits, plateThickness, extendBottom, variant, hangerTolerance,
        offsetX, offsetY, offsetZ,
        rotateX, rotateY, rotateZ,
      }));
    } catch {}
  }

  const saved = loadState();

  // Plate configuration
  let plateUnits = $state(saved?.plateUnits ?? 1);
  let plateThickness = $state(saved?.plateThickness ?? 0);
  let extendBottom = $state(saved?.extendBottom ?? 0);
  let variant = $state(saved?.variant ?? 'Original');
  let hangerTolerance = $state(saved?.hangerTolerance ?? 0.15);

  // Transform values (applied to uploaded model)
  let offsetX = $state(saved?.offsetX ?? 0);
  let offsetY = $state(saved?.offsetY ?? 0);
  let offsetZ = $state(saved?.offsetZ ?? 0);
  let rotateX = $state(saved?.rotateX ?? 0);
  let rotateY = $state(saved?.rotateY ?? 0);
  let rotateZ = $state(saved?.rotateZ ?? 0);

  // Persist state on any change
  $effect(() => {
    plateUnits; plateThickness; extendBottom; variant; hangerTolerance;
    offsetX; offsetY; offsetZ;
    rotateX; rotateY; rotateZ;
    saveState();
  });

  // STL data states
  let plateSTLData = $state(null);
  let uploadedSTLData = $state(null);
  let uploadedFileName = $state('');
  let fusedSTLData = $state(null);
  let fusedFileName = $state('');
  let errorMessage = $state('');
  let isGenerating = $state(false);

  const variantDescription = 'The original variant is compatible with legacy tiles and accessories. The thicker cleats variant shifts the cleat profile back 1mm for 60% higher weight capacity and 10% less filament usage. The two profiles are mechanically incompatible. If starting a new deployment, the thicker cleats variant is recommended.';

  async function fetchPlate() {
    isGenerating = true;
    errorMessage = '';
    try {
      const formData = new FormData();
      formData.append('plate_units', plateUnits);
      formData.append('plate_thickness', plateThickness);
      formData.append('extend_bottom', extendBottom);
      formData.append('variant', variant === 'Original' ? '0' : '1');
      formData.append('hanger_tolerance', hangerTolerance);
      formData.append('offset_x', 0);
      formData.append('offset_y', 0);
      formData.append('offset_z', 0);
      formData.append('rotate_x', 0);
      formData.append('rotate_y', 0);
      formData.append('rotate_z', 0);
      const { blob, filename } = await generateFusedSTL(formData);
      plateSTLData = await blob.arrayBuffer();
      fusedSTLData = null;
    } catch (e) {
      errorMessage = e.message || 'Failed to generate plate';
      console.error('Plate fetch failed:', e);
    } finally {
      isGenerating = false;
    }
  }

  async function handleGenerate() {
    if (!uploadedSTLData) {
      errorMessage = 'Please upload an STL file first';
      return;
    }
    isGenerating = true;
    errorMessage = '';
    try {
      const formData = new FormData();
      const file = new File([uploadedSTLData], uploadedFileName, { type: 'model/stl' });
      formData.append('model', file);
      formData.append('plate_units', plateUnits);
      formData.append('plate_thickness', plateThickness);
      formData.append('extend_bottom', extendBottom);
      formData.append('variant', variant === 'Original' ? '0' : '1');
      formData.append('hanger_tolerance', hangerTolerance);
      formData.append('offset_x', offsetX);
      formData.append('offset_y', offsetY);
      formData.append('offset_z', offsetZ);
      formData.append('rotate_x', rotateX);
      formData.append('rotate_y', rotateY);
      formData.append('rotate_z', rotateZ);
      const { blob, filename } = await generateFusedSTL(formData);
      fusedSTLData = await blob.arrayBuffer();
      fusedFileName = filename;
    } catch (e) {
      errorMessage = e.message || 'Model generation failed';
      console.error('Generate failed:', e);
    } finally {
      isGenerating = false;
    }
  }

  function handleFileLoad({ file, data }) {
    uploadedSTLData = data;
    uploadedFileName = file.name;
    errorMessage = '';
    fetchPlate();
  }

  function handleFileRemove() {
    uploadedSTLData = null;
    uploadedFileName = '';
    fusedSTLData = null;
    offsetX = 0;
    offsetY = 0;
    offsetZ = 0;
    rotateX = 0;
    rotateY = 0;
    rotateZ = 0;
    fetchPlate();
  }

  function handleReset() {
    plateUnits = 1;
    plateThickness = 0;
    extendBottom = 0;
    variant = 'Original';
    hangerTolerance = 0.15;
    offsetX = 0;
    offsetY = 0;
    offsetZ = 0;
    rotateX = 0;
    rotateY = 0;
    rotateZ = 0;
    uploadedSTLData = null;
    uploadedFileName = '';
    fusedSTLData = null;
    errorMessage = '';
    fetchPlate();
  }

  function handleDownload() {
    if (fusedSTLData) {
      const blob = new Blob([fusedSTLData], { type: 'model/stl' });
      downloadSTL(blob, fusedFileName);
    }
  }

  let plateFetchTimeout = null;
  function debouncedFetchPlate() {
    clearTimeout(plateFetchTimeout);
    plateFetchTimeout = setTimeout(() => fetchPlate(), 300);
  }

  onMount(() => {
    fetchPlate();
  });
</script>

<svelte:head>
  <title>Anything GOEWS</title>
</svelte:head>

<main class="bg-gray-100 min-h-screen">
  <div class="bg-gray-800 text-white p-4 mb-6 flex items-center justify-between">
    <h1 class="text-xl font-bold">Anything GOEWS</h1>
    <div class="flex items-center gap-6">
      <a href="https://goews.ws" target="_blank" rel="noopener noreferrer" class="flex items-center space-x-2 hover:text-gray-300">
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
        </svg>
        <span>goews.ws</span>
      </a>
      <a href="https://github.com/jimfunk/anything-goews" target="_blank" rel="noopener noreferrer" class="flex items-center space-x-2 hover:text-gray-300">
        <div class="flex flex-col items-center">
          <svg class="h-6 w-6 fill-white hover:fill-gray-300" aria-hidden="true" viewBox="0 0 16 16" version="1.1">
            <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63.06 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
          </svg>
        </div>
        <span>jimfunk/anything-goews</span>
      </a>
    </div>
  </div>

  <div class="flex flex-col lg:flex-row gap-4 p-4">
    <!-- Parameters Panel -->
    <div class="lg:w-1/3 flex flex-col gap-4">
      {#if errorMessage}
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
          {errorMessage}
        </div>
      {/if}

      <!-- Variant -->
      <div class="bg-white rounded-lg shadow p-4">
        <h2 class="text-lg font-bold mb-2 text-gray-800">Variant</h2>
        <p class="text-gray-500 text-sm mb-3">{variantDescription}</p>
        <select bind:value={variant} onchange={debouncedFetchPlate}
          class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
          <option value="Original">Original</option>
          <option value="Thicker Cleats">Thicker Cleats</option>
        </select>
      </div>

      <!-- Upload -->
      <div class="bg-white rounded-lg shadow p-4">
        <STLUpload
          fileName={uploadedFileName}
          fileload={handleFileLoad}
          remove={handleFileRemove}
          onerror={(msg) => errorMessage = msg}
        />
      </div>

      <!-- Plate Config -->
      <div class="bg-white rounded-lg shadow p-4">
        <PlateConfig
          bind:plateUnits
          bind:plateThickness
          bind:extendBottom
          bind:variant
          bind:hangerTolerance
          onchange={debouncedFetchPlate}
        />
      </div>

      <!-- Transform Controls -->
      <div class="bg-white rounded-lg shadow p-4">
        <TransformControls
          bind:offsetX
          bind:offsetY
          bind:offsetZ
          bind:rotateX
          bind:rotateY
          bind:rotateZ
          disabled={!uploadedSTLData}
        />
      </div>

      <!-- Actions -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex gap-2">
          <button type="button" onclick={handleReset}
            class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50">
            Reset
          </button>
          <button type="button" onclick={handleGenerate} disabled={isGenerating || !uploadedSTLData}
            class="flex-1 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50">
            {isGenerating ? 'Generating...' : 'Generate'}
          </button>
        </div>
      </div>
    </div>

    <!-- Viewer Panel -->
    <div class="lg:w-2/3 bg-white rounded-lg shadow p-4">
      <div class="h-[500px] bg-gray-50 rounded flex items-center justify-center">
        {#if fusedSTLData}
          <STLViewer fusedSTLData={fusedSTLData} />
        {:else if plateSTLData || uploadedSTLData}
          <STLViewer
            plateSTLData={plateSTLData}
            uploadedSTLData={uploadedSTLData}
            {offsetX}
            {offsetY}
            {offsetZ}
            {rotateX}
            {rotateY}
            {rotateZ}
          />
        {:else if isGenerating}
          <div class="text-gray-400 text-center">
            <svg class="w-12 h-12 mx-auto mb-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <p>Generating plate...</p>
          </div>
        {:else}
          <div class="text-gray-400 text-center">
            <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <rect x="3" y="3" width="18" height="18" rx="2" stroke-width="1.5"/>
              <circle cx="8.5" cy="8.5" r="1.5" stroke-width="1.5"/>
              <polyline points="21 15 16 10 5 21" stroke-width="1.5"/>
            </svg>
            <p>Loading...</p>
          </div>
        {/if}
      </div>

      {#if fusedSTLData}
        <button onclick={handleDownload}
          class="mt-4 bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
          Download {fusedFileName}
        </button>
      {/if}

      {#if uploadedSTLData && !fusedSTLData}
        <div class="mt-4 flex justify-center gap-6">
          <span class="flex items-center gap-2 text-sm text-gray-600">
            <span class="w-3 h-3 rounded bg-blue-500 inline-block"></span> Plate
          </span>
          <span class="flex items-center gap-2 text-sm text-gray-600">
            <span class="w-3 h-3 rounded bg-orange-500 inline-block"></span> Uploaded model
          </span>
        </div>
      {/if}
    </div>
  </div>
</main>
