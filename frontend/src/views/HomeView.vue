<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-600 to-indigo-700 flex flex-col items-center justify-center text-white px-4">
    <h1 class="text-4xl font-bold mb-4 text-center">Найди свою профессию</h1>
    <p class="text-blue-100 text-lg mb-10 text-center max-w-xl">
      Пройди тест профессиональных интересов и узнай, какие профессии подходят именно тебе.
    </p>
    <div class="flex gap-4">
      <router-link to="/auth/register" class="bg-white text-blue-600 font-semibold px-6 py-3 rounded-lg hover:bg-blue-50 transition">
        Начать
      </router-link>
      <router-link to="/auth/login" class="border border-white text-white font-semibold px-6 py-3 rounded-lg hover:bg-white/10 transition">
        Войти
      </router-link>
    </div>
  </div>
</template>
