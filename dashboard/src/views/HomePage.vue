<template>
  <div class="min-h-screen bg-[#0a0a0c] text-gray-300 relative overflow-hidden">
    <!-- Ambient background orbs -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden">
      <div class="absolute -top-[20%] -left-[10%] w-[600px] h-[600px] bg-amber-500/[0.07] rounded-full blur-[120px]"></div>
      <div class="absolute top-[40%] -right-[10%] w-[500px] h-[500px] bg-amber-600/[0.05] rounded-full blur-[100px]"></div>
      <div class="absolute -bottom-[10%] left-[20%] w-[400px] h-[400px] bg-amber-700/[0.04] rounded-full blur-[90px]"></div>
    </div>

    <!-- Subtle grid overlay -->
    <div class="fixed inset-0 pointer-events-none opacity-[0.015]" style="background-image: linear-gradient(rgba(245, 158, 11, 0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(245, 158, 11, 0.3) 1px, transparent 1px); background-size: 60px 60px;"></div>

    <!-- Nav -->
    <nav class="relative z-10 max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <span class="text-xl">🦊</span>
        <span class="text-lg font-semibold text-gray-100 tracking-tight">Kitsune</span>
      </div>
      <div class="flex items-center gap-6">
        <a href="#features" class="text-sm text-gray-400 hover:text-amber-400 transition-colors duration-200">Features</a>
        <a href="#how-it-works" class="text-sm text-gray-400 hover:text-amber-400 transition-colors duration-200">How it works</a>
        <a href="#pricing" class="text-sm text-gray-400 hover:text-amber-400 transition-colors duration-200">Pricing</a>
        <a
          href="https://github.com/sagnik3788/kitsune"
          target="_blank"
          class="text-sm text-gray-400 hover:text-amber-400 transition-colors duration-200 flex items-center gap-1.5"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd"/>
          </svg>
          GitHub
        </a>
        <router-link
          to="/workflows"
          class="text-sm font-medium text-amber-400 hover:text-amber-300 transition-colors duration-200"
        >
          Dashboard →
        </router-link>
      </div>
    </nav>

    <!-- Hero -->
    <section class="relative z-10 min-h-[calc(100vh-80px)] flex flex-col items-center justify-center pt-16 pb-24 md:pt-20 md:pb-32">
      <div class="max-w-6xl mx-auto px-4 text-center">
        <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-medium tracking-wide mb-8">
          Your agent's least favorite app
        </div>

        <h1 class="text-5xl md:text-7xl font-bold text-gray-100 tracking-tight mb-6 leading-[1.1]">
          Control Your
          <span class="bg-gradient-to-r from-amber-300 via-amber-400 to-amber-500 bg-clip-text text-transparent">AI Agents</span>
        </h1>

        <p class="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-12 leading-relaxed">
          A state machine harness that locks tools and skills to phases for AI agents.
        </p>

        <div class="flex items-center justify-center gap-4 mb-16">
          <router-link
            to="/workflows"
            class="group inline-flex items-center px-7 py-3.5 bg-amber-500 hover:bg-amber-400 text-[#0a0a0c] font-semibold rounded-xl transition-all duration-200 shadow-[0_0_20px_rgba(245,158,11,0.15)] hover:shadow-[0_0_30px_rgba(245,158,11,0.25)] hover:-translate-y-0.5"
          >
            Get Started
            <svg class="w-4 h-4 ml-2 transition-transform duration-200 group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
            </svg>
          </router-link>
          <a
            href="#how-it-works"
            class="inline-flex items-center px-7 py-3.5 border border-[#2a2a30] hover:border-amber-500/40 text-gray-300 hover:text-gray-100 rounded-xl transition-all duration-200 hover:-translate-y-0.5"
          >
            Learn More
          </a>
        </div>

        <div class="relative max-w-5xl mx-auto">
          <div class="absolute -inset-1 bg-gradient-to-t from-amber-500/20 to-transparent rounded-2xl blur-2xl"></div>
          <img
            src="/dashboard.jpeg"
            alt="Kitsune visual workflow editor showing phases, tools, and transitions"
            class="relative w-full rounded-xl border border-[#2a2a30] shadow-2xl shadow-black/40"
          />
        </div>
      </div>

      <!-- Scroll indicator -->
      <div class="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-gray-500 animate-bounce">
        <span class="text-xs">Scroll</span>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
        </svg>
      </div>
    </section>

    <!-- Features -->
    <section id="features" class="relative z-10 py-24 md:py-32 border-t border-[#15151a]">
      <div class="max-w-6xl mx-auto px-4">
        <div class="text-center mb-16">
          <p class="text-amber-400 text-sm font-medium tracking-wide uppercase mb-3">Features</p>
          <h2 class="text-3xl md:text-4xl font-bold text-gray-100 tracking-tight">Hard guardrails. Soft limits.</h2>
          <p class="text-gray-400 mt-4 max-w-2xl mx-auto">Stop trusting prompts to keep your agents in line. Enforce the rules at runtime.</p>
        </div>

        <div class="grid md:grid-cols-2 gap-6">
          <div class="group relative bg-[#111116] border border-[#1e1e24] rounded-2xl p-7 hover:border-amber-500/30 transition-all duration-300 hover:-translate-y-1">
            <div class="absolute inset-0 rounded-2xl bg-gradient-to-b from-amber-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            <div class="relative">
              <div class="w-11 h-11 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-5 group-hover:bg-amber-500/15 transition-colors duration-300">
                <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
              </div>
              <h3 class="font-semibold text-gray-100 text-lg mb-2">Phase-Locked Tool Access</h3>
              <p class="text-sm text-gray-400 leading-relaxed">
                Each workflow phase declares exactly which tools are available. Everything else is blocked at the protocol level.
              </p>
            </div>
          </div>

          <div class="group relative bg-[#111116] border border-[#1e1e24] rounded-2xl p-7 hover:border-amber-500/30 transition-all duration-300 hover:-translate-y-1">
            <div class="absolute inset-0 rounded-2xl bg-gradient-to-b from-amber-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            <div class="relative">
              <div class="w-11 h-11 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-5 group-hover:bg-amber-500/15 transition-colors duration-300">
                <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
              <h3 class="font-semibold text-gray-100 text-lg mb-2">Transition Triggers</h3>
              <p class="text-sm text-gray-400 leading-relaxed">
                Agents move between phases only by emitting the right trigger. No accidental escapes, no hidden state jumps.
              </p>
            </div>
          </div>

          <div class="group relative bg-[#111116] border border-[#1e1e24] rounded-2xl p-7 hover:border-amber-500/30 transition-all duration-300 hover:-translate-y-1">
            <div class="absolute inset-0 rounded-2xl bg-gradient-to-b from-amber-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            <div class="relative">
              <div class="w-11 h-11 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-5 group-hover:bg-amber-500/15 transition-colors duration-300">
                <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
              </div>
              <h3 class="font-semibold text-gray-100 text-lg mb-2">Run History & Observability</h3>
              <p class="text-sm text-gray-400 leading-relaxed">
                Every tool call, transition, and decision is logged. Know exactly what your agent did and why.
              </p>
            </div>
          </div>

          <div class="group relative bg-[#111116] border border-[#1e1e24] rounded-2xl p-7 hover:border-amber-500/30 transition-all duration-300 hover:-translate-y-1">
            <div class="absolute inset-0 rounded-2xl bg-gradient-to-b from-amber-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            <div class="relative">
              <div class="w-11 h-11 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-5 group-hover:bg-amber-500/15 transition-colors duration-300">
                <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
                </svg>
              </div>
              <h3 class="font-semibold text-gray-100 text-lg mb-2">MCP Gateway</h3>
              <p class="text-sm text-gray-400 leading-relaxed">
                Drop Kitsune between your agent and its tools via MCP. Enforce workflows without rewriting agent code.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section id="how-it-works" class="relative z-10 py-24 md:py-32 border-t border-[#15151a]">
      <div class="max-w-6xl mx-auto px-4">
        <div class="text-center mb-16">
          <p class="text-amber-400 text-sm font-medium tracking-wide uppercase mb-3">How it works</p>
          <h2 class="text-3xl md:text-4xl font-bold text-gray-100 tracking-tight">Three steps to agent discipline</h2>
        </div>

        <div class="grid md:grid-cols-3 gap-6">
          <div class="group relative bg-[#111116] border border-[#1e1e24] rounded-2xl p-7 hover:border-amber-500/30 transition-all duration-300 hover:-translate-y-1">
            <div class="absolute inset-0 rounded-2xl bg-gradient-to-b from-amber-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            <div class="relative">
              <div class="w-11 h-11 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-5 group-hover:bg-amber-500/15 transition-colors duration-300">
                <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                </svg>
              </div>
              <h3 class="font-semibold text-gray-100 text-lg mb-2">Define Phases</h3>
              <p class="text-sm text-gray-400 leading-relaxed">
                Plan &rarr; Implement &rarr; Test. Each phase has allowed tools and transition triggers.
              </p>
            </div>
          </div>

          <div class="group relative bg-[#111116] border border-[#1e1e24] rounded-2xl p-7 hover:border-amber-500/30 transition-all duration-300 hover:-translate-y-1">
            <div class="absolute inset-0 rounded-2xl bg-gradient-to-b from-amber-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            <div class="relative">
              <div class="w-11 h-11 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-5 group-hover:bg-amber-500/15 transition-colors duration-300">
                <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
              </div>
              <h3 class="font-semibold text-gray-100 text-lg mb-2">Lock Tools</h3>
              <p class="text-sm text-gray-400 leading-relaxed">
                Agents can only call tools available in their current phase. No flailing, no escape.
              </p>
            </div>
          </div>

          <div class="group relative bg-[#111116] border border-[#1e1e24] rounded-2xl p-7 hover:border-amber-500/30 transition-all duration-300 hover:-translate-y-1">
            <div class="absolute inset-0 rounded-2xl bg-gradient-to-b from-amber-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            <div class="relative">
              <div class="w-11 h-11 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-5 group-hover:bg-amber-500/15 transition-colors duration-300">
                <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
              </div>
              <h3 class="font-semibold text-gray-100 text-lg mb-2">Track Everything</h3>
              <p class="text-sm text-gray-400 leading-relaxed">
                Full audit trail of every tool call, transition, and decision. Know exactly what happened.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Built-in templates -->
    <section id="templates" class="relative z-10 py-24 md:py-32 border-t border-[#15151a]">
      <div class="max-w-6xl mx-auto px-4">
        <div class="text-center mb-16">
          <p class="text-amber-400 text-sm font-medium tracking-wide uppercase mb-3">Templates</p>
          <h2 class="text-3xl md:text-4xl font-bold text-gray-100 tracking-tight">Start with a proven workflow</h2>
        </div>

        <div class="grid md:grid-cols-3 gap-6">
          <div class="group relative bg-[#111116] border border-[#1e1e24] rounded-2xl p-7 hover:border-amber-500/30 transition-all duration-300 hover:-translate-y-1">
            <div class="absolute inset-0 rounded-2xl bg-gradient-to-b from-amber-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            <div class="relative">
              <div class="text-xs font-medium text-amber-500/60 mb-3 tracking-wide uppercase">Bugfix</div>
              <h3 class="font-semibold text-gray-100 text-lg mb-2">Bug Fix Loop</h3>
              <p class="text-sm text-gray-400 leading-relaxed mb-4">
                Plan → Implement → Test → Review. Classic debugging with rollback guard.
              </p>
              <div class="flex flex-wrap gap-2">
                <span class="text-xs bg-amber-500/10 text-amber-400 px-2 py-1 rounded">plan</span>
                <span class="text-xs bg-amber-500/10 text-amber-400 px-2 py-1 rounded">implement</span>
                <span class="text-xs bg-amber-500/10 text-amber-400 px-2 py-1 rounded">test</span>
                <span class="text-xs bg-amber-500/10 text-amber-400 px-2 py-1 rounded">review</span>
              </div>
            </div>
          </div>

          <div class="group relative bg-[#111116] border border-[#1e1e24] rounded-2xl p-7 hover:border-amber-500/30 transition-all duration-300 hover:-translate-y-1">
            <div class="absolute inset-0 rounded-2xl bg-gradient-to-b from-amber-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            <div class="relative">
              <div class="text-xs font-medium text-amber-500/60 mb-3 tracking-wide uppercase">Feature</div>
              <h3 class="font-semibold text-gray-100 text-lg mb-2">Feature Development</h3>
              <p class="text-sm text-gray-400 leading-relaxed mb-4">
                Spec → Design → Implement → Test → Review → Deploy. Full product flow.
              </p>
              <div class="flex flex-wrap gap-2">
                <span class="text-xs bg-amber-500/10 text-amber-400 px-2 py-1 rounded">spec</span>
                <span class="text-xs bg-amber-500/10 text-amber-400 px-2 py-1 rounded">design</span>
                <span class="text-xs bg-amber-500/10 text-amber-400 px-2 py-1 rounded">deploy</span>
              </div>
            </div>
          </div>

          <div class="group relative bg-[#111116] border border-[#1e1e24] rounded-2xl p-7 hover:border-amber-500/30 transition-all duration-300 hover:-translate-y-1">
            <div class="absolute inset-0 rounded-2xl bg-gradient-to-b from-amber-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            <div class="relative">
              <div class="text-xs font-medium text-amber-500/60 mb-3 tracking-wide uppercase">Security</div>
              <h3 class="font-semibold text-gray-100 text-lg mb-2">Security Audit</h3>
              <p class="text-sm text-gray-400 leading-relaxed mb-4">
                Recon → Analyze → Exploit → Fix → Verify → Report. Penetration testing flow.
              </p>
              <div class="flex flex-wrap gap-2">
                <span class="text-xs bg-amber-500/10 text-amber-400 px-2 py-1 rounded">recon</span>
                <span class="text-xs bg-amber-500/10 text-amber-400 px-2 py-1 rounded">exploit</span>
                <span class="text-xs bg-amber-500/10 text-amber-400 px-2 py-1 rounded">verify</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing -->
    <section id="pricing" class="relative z-10 py-24 md:py-32 border-t border-[#15151a]">
      <div class="max-w-6xl mx-auto px-4">
        <div class="text-center mb-16">
          <p class="text-amber-400 text-sm font-medium tracking-wide uppercase mb-3">Pricing</p>
          <h2 class="text-3xl md:text-4xl font-bold text-gray-100 tracking-tight">Simple, transparent pricing</h2>
        </div>

        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <div class="group relative bg-[#111116] border border-[#1e1e24] rounded-2xl p-7 flex flex-col hover:border-[#2a2a30] transition-all duration-300">
            <div class="mb-6">
              <h3 class="font-semibold text-gray-100 text-lg mb-1">Free</h3>
              <div class="flex items-baseline gap-1">
                <span class="text-3xl font-bold text-gray-100">$0</span>
              </div>
            </div>
            <ul class="text-sm text-gray-400 space-y-3 mb-8 flex-1">
              <li class="flex items-center gap-2.5">
                <svg class="w-4 h-4 text-amber-500/60 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                3 workflows
              </li>
              <li class="flex items-center gap-2.5">
                <svg class="w-4 h-4 text-amber-500/60 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                200 transitions/mo
              </li>
              <li class="flex items-center gap-2.5">
                <svg class="w-4 h-4 text-amber-500/60 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                72-hour history
              </li>
            </ul>
            <router-link to="/workflows" class="w-full text-center px-4 py-2.5 border border-[#2a2a30] hover:border-amber-500/40 text-gray-300 hover:text-gray-100 rounded-xl transition-all duration-200 text-sm font-medium">
              Get Started
            </router-link>
          </div>

          <div class="group relative bg-[#111116] border border-amber-500/30 rounded-2xl p-7 flex flex-col shadow-[0_0_30px_rgba(245,158,11,0.06)]">
            <div class="absolute -top-3 left-1/2 -translate-x-1/2 px-3.5 py-1 bg-gradient-to-r from-amber-400 to-amber-500 text-[#0a0a0c] text-xs font-bold rounded-full shadow-lg">
              Popular
            </div>
            <div class="mb-6">
              <h3 class="font-semibold text-gray-100 text-lg mb-1">Pro</h3>
              <div class="flex items-baseline gap-1">
                <span class="text-3xl font-bold text-gray-100">$5</span>
                <span class="text-sm text-gray-500">/mo</span>
              </div>
            </div>
            <ul class="text-sm text-gray-400 space-y-3 mb-8 flex-1">
              <li class="flex items-center gap-2.5">
                <svg class="w-4 h-4 text-amber-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                10 workflows
              </li>
              <li class="flex items-center gap-2.5">
                <svg class="w-4 h-4 text-amber-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                2,500 transitions/mo
              </li>
              <li class="flex items-center gap-2.5">
                <svg class="w-4 h-4 text-amber-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                7-day history
              </li>
            </ul>
            <router-link to="/workflows" class="w-full text-center px-4 py-2.5 bg-amber-500 hover:bg-amber-400 text-[#0a0a0c] rounded-xl transition-all duration-200 text-sm font-semibold shadow-[0_0_15px_rgba(245,158,11,0.2)] hover:shadow-[0_0_20px_rgba(245,158,11,0.3)]">
              Get Started
            </router-link>
          </div>

          <div class="group relative bg-[#111116] border border-[#1e1e24] rounded-2xl p-7 flex flex-col hover:border-[#2a2a30] transition-all duration-300">
            <div class="mb-6">
              <h3 class="font-semibold text-gray-100 text-lg mb-1">Team</h3>
              <div class="flex items-baseline gap-1">
                <span class="text-3xl font-bold text-gray-100">$10</span>
                <span class="text-sm text-gray-500">/mo</span>
              </div>
            </div>
            <ul class="text-sm text-gray-400 space-y-3 mb-8 flex-1">
              <li class="flex items-center gap-2.5">
                <svg class="w-4 h-4 text-amber-500/60 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                30 workflows
              </li>
              <li class="flex items-center gap-2.5">
                <svg class="w-4 h-4 text-amber-500/60 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                10,000 transitions/mo
              </li>
              <li class="flex items-center gap-2.5">
                <svg class="w-4 h-4 text-amber-500/60 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                90-day history
              </li>
            </ul>
            <router-link to="/workflows" class="w-full text-center px-4 py-2.5 border border-[#2a2a30] hover:border-amber-500/40 text-gray-300 hover:text-gray-100 rounded-xl transition-all duration-200 text-sm font-medium">
              Get Started
            </router-link>
          </div>

          <div class="group relative bg-[#111116] border border-[#1e1e24] rounded-2xl p-7 flex flex-col hover:border-[#2a2a30] transition-all duration-300">
            <div class="mb-6">
              <h3 class="font-semibold text-gray-100 text-lg mb-1">Self-Host</h3>
              <div class="flex items-baseline gap-1">
                <span class="text-3xl font-bold text-gray-100">Free</span>
              </div>
            </div>
            <ul class="text-sm text-gray-400 space-y-3 mb-8 flex-1">
              <li class="flex items-center gap-2.5">
                <svg class="w-4 h-4 text-amber-500/60 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                Unlimited workflows
              </li>
              <li class="flex items-center gap-2.5">
                <svg class="w-4 h-4 text-amber-500/60 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                Unlimited transitions
              </li>
              <li class="flex items-center gap-2.5">
                <svg class="w-4 h-4 text-amber-500/60 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                Unlimited history
              </li>
              <li class="flex items-center gap-2.5">
                <svg class="w-4 h-4 text-amber-500/60 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                Your own infrastructure
              </li>
            </ul>
            <a href="#" class="w-full text-center px-4 py-2.5 border border-[#2a2a30] hover:border-amber-500/40 text-gray-300 hover:text-gray-100 rounded-xl transition-all duration-200 text-sm font-medium cursor-default">
              Coming Soon
            </a>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="relative z-10 py-24 md:py-32 border-t border-[#15151a]">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <div class="relative bg-gradient-to-b from-amber-500/10 to-transparent border border-amber-500/20 rounded-3xl p-10 md:p-16">
          <div class="absolute inset-0 rounded-3xl bg-[#111116]/50"></div>
          <div class="relative">
            <h2 class="text-3xl md:text-4xl font-bold text-gray-100 tracking-tight mb-4">Ready to stop the flailing?</h2>
            <p class="text-gray-400 mb-8 max-w-xl mx-auto">
              Define your first workflow in minutes. Lock tools to phases. Watch your agent stay in bounds.
            </p>
            <router-link
              to="/workflows"
              class="group inline-flex items-center px-8 py-4 bg-amber-500 hover:bg-amber-400 text-[#0a0a0c] font-semibold rounded-xl transition-all duration-200 shadow-[0_0_30px_rgba(245,158,11,0.2)] hover:shadow-[0_0_40px_rgba(245,158,11,0.3)] hover:-translate-y-0.5"
            >
              Create Your First Workflow
              <svg class="w-4 h-4 ml-2 transition-transform duration-200 group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
              </svg>
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="relative z-10 border-t border-[#15151a] py-10">
      <div class="max-w-6xl mx-auto px-4 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-sm">🦊</span>
          <p class="text-sm text-gray-500">Built for the opencode ecosystem</p>
        </div>
        <a href="https://github.com/sagnik3788/kitsune" target="_blank" class="text-sm text-gray-400 hover:text-amber-400 transition-colors duration-200 flex items-center gap-2">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd"/>
          </svg>
          GitHub
        </a>
      </div>
    </footer>
  </div>
</template>
