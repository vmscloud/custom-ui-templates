<template>
  <div class="home-view">
    <h2>개발용 홈</h2>
    <p>아래 메뉴 중 하나를 선택하여 테스트하세요:</p>
    <nav>
      <router-link to="/custom-menu-1">CustomMenu1</router-link>
      <router-link to="/item-master">ItemMaster</router-link>
      <router-link to="/item-master-wijmo">ItemMaster Wijmo</router-link>
    </nav>
  </div>
</template>

<script setup lang="ts">
// 개발용 홈 뷰
</script>

<style scoped>
.home-view {
  padding: 2rem;
}

nav {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

nav a {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  text-decoration: none;
  border-radius: 0.375rem;
  transition: background 0.2s;
}

nav a:hover {
  background: #2563eb;
}
</style>
