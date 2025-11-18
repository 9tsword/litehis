<template>
  <section class="section-card">
    <header class="section-card__header">
      <div>
        <h2>{{ title }}</h2>
        <p v-if="subtitle" class="section-card__subtitle">{{ subtitle }}</p>
      </div>
      <slot name="actions"></slot>
    </header>
    <div class="section-card__body">
      <slot></slot>
    </div>
  </section>
</template>

<script setup lang="ts">
interface Props {
  title: string;
  subtitle?: string;
}

defineProps<Props>();
</script>

<style scoped>
.section-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(50, 76, 140, 0.12);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  backdrop-filter: blur(6px);
}

.section-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.section-card__header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #14213d;
}

.section-card__subtitle {
  margin: 0;
  color: #4f5d75;
  font-size: 0.875rem;
}

.section-card__body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
