<script>
  let {
    label = '',
    id = '',
    value = $bindable(0),
    min = -Infinity,
    max = Infinity,
    steps = [],
    help = '',
    disabled = false,
    transform = null
  } = $props();

  function adjust(delta) {
    let newValue = value + delta;
    if (transform) {
      newValue = transform(newValue);
    }
    value = Math.round(Math.max(min, Math.min(max, newValue)) * 100) / 100;
  }
</script>

<div class="space-y-1">
  <label for={id} class="block text-gray-700 text-sm font-bold">{label}</label>
  <input
    type="number"
    {id}
    bind:value
    {min}
    {max}
    {disabled}
    step={steps[0]?.value ?? 1}
    class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline disabled:bg-gray-100"
  />
  <div class="grid grid-cols-4 gap-2">
    {#each steps as step}
      <div class="flex items-center rounded-md overflow-hidden border border-gray-300">
        <span class="flex-1 bg-gray-100 text-sm text-gray-700 text-center py-2 tabular-nums select-none font-semibold">{step.label}</span>
        <button
          onclick={() => adjust(-step.value)}
          {disabled}
          class="w-9 bg-white hover:bg-gray-100 text-gray-600 text-lg font-bold py-2 disabled:opacity-40 disabled:cursor-not-allowed transition-colors border-l border-gray-300"
          aria-label="Decrease by {step.label}"
        >▼</button>
        <button
          onclick={() => adjust(step.value)}
          {disabled}
          class="w-9 bg-white hover:bg-blue-50 text-blue-600 text-lg font-bold py-2 disabled:opacity-40 disabled:cursor-not-allowed transition-colors border-l border-gray-300"
          aria-label="Increase by {step.label}"
        >▲</button>
      </div>
    {/each}
  </div>
  {#if help}
    <p class="text-gray-500 text-xs mt-1">{help}</p>
  {/if}
</div>
