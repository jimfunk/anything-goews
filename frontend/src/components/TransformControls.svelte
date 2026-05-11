<script>
  import NumberInput from './NumberInput.svelte';

  let {
    offsetX = $bindable(0),
    offsetY = $bindable(0),
    offsetZ = $bindable(0),
    rotateX = $bindable(0),
    rotateY = $bindable(0),
    rotateZ = $bindable(0),
    disabled = false
  } = $props();

  function wrapRotation(v) {
    v = v % 360;
    return v < 0 ? v + 360 : v;
  }

  const positionSteps = [
    { value: 0.1, label: '0.1' },
    { value: 1, label: '1' },
    { value: 10, label: '10' },
    { value: 50, label: '50' },
  ];

  const rotationSteps = [
    { value: 90, label: '90°' },
  ];
</script>

<div class="space-y-4">
  <!-- Position -->
  <div>
    <h3 class="text-sm font-semibold text-gray-600 border-b border-gray-200 pb-1 mb-3">Position (mm)</h3>
    <div class="space-y-3">
      <NumberInput
        id="pos-x"
        label="X"
        bind:value={offsetX}
        steps={positionSteps}
        buttonClass="grid grid-cols-4 gap-1"
        {disabled}
      />
      <NumberInput
        id="pos-y"
        label="Y"
        bind:value={offsetY}
        steps={positionSteps}
        buttonClass="grid grid-cols-4 gap-1"
        {disabled}
      />
      <NumberInput
        id="pos-z"
        label="Z"
        bind:value={offsetZ}
        steps={positionSteps}
        buttonClass="grid grid-cols-4 gap-1"
        {disabled}
      />
    </div>
  </div>

  <!-- Rotation -->
  <div>
    <h3 class="text-sm font-semibold text-gray-600 border-b border-gray-200 pb-1 mb-3">Rotation (degrees)</h3>
    <div class="space-y-3">
      <NumberInput
        id="rot-x"
        label="X"
        bind:value={rotateX}
        min={0}
        max={360}
        steps={rotationSteps}
        buttonClass="grid grid-cols-2 gap-1"
        {disabled}
        transform={wrapRotation}
      />
      <NumberInput
        id="rot-y"
        label="Y"
        bind:value={rotateY}
        min={0}
        max={360}
        steps={rotationSteps}
        buttonClass="grid grid-cols-2 gap-1"
        {disabled}
        transform={wrapRotation}
      />
      <NumberInput
        id="rot-z"
        label="Z"
        bind:value={rotateZ}
        min={0}
        max={360}
        steps={rotationSteps}
        buttonClass="grid grid-cols-2 gap-1"
        {disabled}
        transform={wrapRotation}
      />
    </div>
  </div>
</div>
