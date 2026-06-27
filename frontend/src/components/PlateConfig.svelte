<script>
  import NumberInput from './NumberInput.svelte';

  let {
    plateUnits = $bindable(1),
    plateThickness = $bindable(0),
    extendBottom = $bindable(0),
    variant = $bindable('Original'),
    hangerTolerance = $bindable(0.15),
    boltNotch = $bindable(true),
    boltNotchThickness = $bindable(3),
    onchange = () => {}
  } = $props();

  $effect(() => {
    plateUnits;
    plateThickness;
    extendBottom;
    variant;
    hangerTolerance;
    boltNotch;
    boltNotchThickness;
    onchange();
  });
</script>

<div class="space-y-4">
  <NumberInput
    label="Plate Units"
    id="plate-units"
    bind:value={plateUnits}
    min={1}
    steps={[{ value: 1, label: '1' }]}
    help="Number of 42mm-wide hanger units"
  />

  <NumberInput
    label="Plate Thickness (mm)"
    id="plate-thickness"
    bind:value={plateThickness}
    min={0}
    steps={[{ value: 0.5, label: '0.5' }, { value: 1, label: '1' }]}
    help="Thickness of the mounting plate"
  />

  <NumberInput
    label="Extend Bottom (mm)"
    id="extend-bottom"
    bind:value={extendBottom}
    min={0}
    steps={[{ value: 1, label: '1' }, { value: 5, label: '5' }]}
    help="Extends the bottom edge downward for extra material"
  />

  <NumberInput
    label="Hanger Tolerance (mm)"
    id="tolerance"
    bind:value={hangerTolerance}
    min={0}
    max={1}
    steps={[{ value: 0.05, label: '0.05' }, { value: 0.1, label: '0.1' }]}
    help="Cleat clearance for looser or tighter fit"
  />

  <div class="flex items-center gap-3">
    <label class="relative inline-flex items-center cursor-pointer">
      <input type="checkbox" bind:checked={boltNotch} class="sr-only peer" />
      <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-500"></div>
    </label>
    <span class="text-gray-700 text-sm font-bold">Bolt Notch</span>
  </div>

  {#if boltNotch}
    <NumberInput
      label="Bolt Notch Thickness (mm)"
      id="bolt-notch-thickness"
      bind:value={boltNotchThickness}
      min={0}
      steps={[{ value: 0.5, label: '0.5' }, { value: 1, label: '1' }]}
      help="Thickness of bolt notch shoulder"
    />
  {/if}
</div>
