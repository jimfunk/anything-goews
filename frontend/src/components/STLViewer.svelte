<script>
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

  let {
    plateSTLData = null,
    uploadedSTLData = null,
    fusedSTLData = null,
    offsetX = 0,
    offsetY = 0,
    offsetZ = 0,
    rotateX = 0,
    rotateY = 0,
    rotateZ = 0
  } = $props();

  let container;
  let scene, camera, renderer, controls;
  let plateMesh = null;
  let uploadedMesh = null;
  let isInitialized = $state(false);
  let hasEverLoadedData = false;

  function disposeMesh(mesh) {
    if (!mesh) return;
    scene.remove(mesh);
    mesh.geometry.dispose();
    mesh.material.dispose();
  }

  function createMesh(geometry, color) {
    geometry.computeVertexNormals();
    const material = new THREE.MeshStandardMaterial({
      color,
      metalness: 0.3,
      roughness: 0.7,
      side: THREE.DoubleSide,
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    return mesh;
  }

  function loadMeshFromData(data, color) {
    const loader = new STLLoader();
    const geometry = loader.parse(data);
    // STL files use Z-up. Three.js uses Y-up.
    // Rotate -90° around X to convert so the model stands upright.
    geometry.rotateX(-Math.PI / 2);
    return createMesh(geometry, color);
  }

  function fitCamera() {
    // Fit to meshes only, excluding the grid
    const box = new THREE.Box3();
    scene.traverse((obj) => {
      if (obj.isMesh) box.expandByObject(obj);
    });
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z, 1);
    const fov = camera.fov * (Math.PI / 180);
    let cameraZ = (maxDim / 2) / Math.tan(fov / 2);
    cameraZ *= 1.5;
    const center = box.getCenter(new THREE.Vector3());
    camera.position.set(
      center.x + cameraZ * 0.7,
      center.y + cameraZ * 0.5,
      center.z + cameraZ
    );
    camera.lookAt(center);
    controls.target.copy(center);
    controls.update();
  }

  function buildScene() {
    if (!isInitialized) return;

    const isFirstLoad = !hasEverLoadedData;

    // Clear existing meshes
    disposeMesh(plateMesh);
    disposeMesh(uploadedMesh);
    plateMesh = null;
    uploadedMesh = null;

    if (fusedSTLData) {
      const fusedMesh = loadMeshFromData(fusedSTLData, 0x3498db);
      scene.add(fusedMesh);
      plateMesh = fusedMesh;
    } else {
      if (plateSTLData) {
        plateMesh = loadMeshFromData(plateSTLData, 0x3498db);
        scene.add(plateMesh);
      }
      if (uploadedSTLData) {
        uploadedMesh = loadMeshFromData(uploadedSTLData, 0xe67e22);
        updateUploadedTransform();
        scene.add(uploadedMesh);
      }
    }

    // Mark that we've loaded data if there's a mesh
    if (plateMesh || uploadedMesh) {
      hasEverLoadedData = true;
    }

    // Only fit camera on the very first successful data load
    if (isFirstLoad && (plateMesh || uploadedMesh)) {
      fitCamera();
    }
  }

  function updateUploadedTransform() {
    if (!uploadedMesh) return;
    uploadedMesh.rotation.set(
      THREE.MathUtils.degToRad(rotateX),
      THREE.MathUtils.degToRad(rotateY),
      THREE.MathUtils.degToRad(rotateZ)
    );
    uploadedMesh.position.set(offsetX, offsetY, offsetZ);
  }

  // Setup scene on mount
  onMount(() => {
    if (!container) return;

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xffffff);

    const width = container.clientWidth;
    const height = container.clientHeight;

    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(50, 100, 50);
    scene.add(directionalLight);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    const grid = new THREE.GridHelper(200, 20, 0xcccccc, 0xe8e8e8);
    scene.add(grid);

    isInitialized = true;
    buildScene();

    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    function handleResize() {
      const w = container.clientWidth;
      const h = container.clientHeight;
      if (w === 0 || h === 0) return;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (renderer) {
        renderer.dispose();
        renderer.domElement.remove();
      }
      if (controls) controls.dispose();
    };
  });

  // React to data changes — rebuild scene when any data prop changes
  $effect(() => {
    // Use props in an expression so compiler tracks them as dependencies
    const data = plateSTLData || uploadedSTLData || fusedSTLData;
    if (isInitialized) buildScene();
  });

  // React to transform changes — update uploaded mesh in place (no rebuild)
  $effect(() => {
    if (isInitialized && uploadedMesh && !fusedSTLData) {
      updateUploadedTransform();
    }
  });
</script>

<div bind:this={container} class="w-full h-full min-h-[500px]"></div>
