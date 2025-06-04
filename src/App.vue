<template>
  <v-app>
    <v-navigation-drawer
      v-model="drawer"
      app
      :permanent="false"
      :width="240"
    >
      <v-list>
        <v-list-item
          v-for="item in menuList"
          :key="item.path"
          :title="item.title"
          @click="navigate(item.path)"
          :active="isActive(item.path)"
        />
      </v-list>
    </v-navigation-drawer>

    <v-app-bar app color="primary" dark>
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <v-app-bar-title>GPU 클러스터 관리자</v-app-bar-title>
    </v-app-bar>

    <v-main>
        <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const drawer = ref(false)  // <- Toggle variable

const router = useRouter()
const route = useRoute()

const menuList = [
 { title: '대시보드', path: '/board' },
 { title: '자원 관리', path: '/resources' },
 { title: '사용자 관리', path: '/users' },
 { title: '보고서', path: '/reports' }
]

function navigate(path) {
 if (route.path !== path) {
    router.push(path)
    drawer.value = false // 메뉴 클릭시 닫고 싶으면 이 줄 추가
  }
}

function isActive(path) {
 return route.path === path
}
</script>