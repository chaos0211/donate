<template>
  <div class="min-h-[calc(100vh-64px)] flex items-center justify-center bg-gradient-to-br from-primary/5 to-secondary/5 p-4">
    <div class="w-full max-w-md card p-6">
      <h1 class="text-xl font-bold mb-4">登录</h1>
      <form class="space-y-3" @submit.prevent="onSubmit">
        <input v-model="username" type="text" placeholder="用户名" class="w-full border rounded px-3 py-2" />
        <input v-model="password" type="password" placeholder="密码" class="w-full border rounded px-3 py-2" />
        <button class="w-full bg-primary text-white py-2 rounded">登录</button>
      </form>
      <p class="text-sm text-info mt-4">没有账户？<router-link to="/register" class="text-primary">去注册</router-link></p>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import http from "@/api/http";

const router = useRouter();
const username = ref("");
const password = ref("");
const loading = ref(false);

async function onSubmit() {
  if (!username.value || !password.value) {
    alert("请输入用户名和密码");
    return;
  }
  loading.value = true;
  try {
    const { data } = await http.post("/api/v1/auth/login", {
      username: username.value,
      password: password.value,
    });
    // 前端持久化一个登录标记；后端接口仍可独立校验用户
    localStorage.setItem("session_user", data.username);
    router.push("/cockpit");
  } catch (e: any) {
    const msg = e?.response?.data?.detail || "登录失败";
    alert(msg);
  } finally {
    loading.value = false;
  }
}
</script>
