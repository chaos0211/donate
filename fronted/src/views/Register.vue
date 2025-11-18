<template>
  <div class="min-h-[calc(100vh-64px)] flex items-center justify-center bg-gray-50 p-4">
    <div class="card p-6 max-w-md w-full">
      <h1 class="text-xl font-bold mb-4">用户注册</h1>
      <form class="space-y-3" @submit.prevent="onSubmit">
        <input v-model="username" type="text" placeholder="用户名" class="w-full border rounded px-3 py-2" />
        <div class="w-full">
          <select v-model="role" class="w-full border rounded px-3 py-2 text-sm">
            <option disabled value="">角色选择</option>
            <option value="donor">普通用户</option>
            <option value="org">公益组织</option>
            <option value="admin">管理员</option>
          </select>
        </div>
        <input v-model="pwd" type="password" placeholder="密码" class="w-full border rounded px-3 py-2" />
        <input v-model="confirm" type="password" placeholder="确认密码" class="w-full border rounded px-3 py-2" />
        <button class="w-full bg-primary text-white py-2 rounded">注册</button>
      </form>
      <p class="text-sm text-info mt-4">已有账户？<router-link to="/login" class="text-primary">立即登录</router-link></p>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import http from "@/api/http";

const router = useRouter();
const username = ref("");
const role = ref("donor");
const pwd = ref("");
const confirm = ref("");

async function onSubmit() {
  if (!username.value || !pwd.value || !confirm.value) {
    alert("请完整填写必填项");
    return;
  }
  if (pwd.value !== confirm.value) {
    alert("两次输入的密码不一致");
    return;
  }
  try {
    await http.post("/api/v1/auth/register", {
      username: username.value,
      password: pwd.value,
      role: role.value,
    });
    alert("注册成功，前往登录");
    router.push("/login");
  } catch (e: any) {
    const msg = e?.response?.data?.detail || "注册失败";
    alert(msg);
  }
}
</script>
