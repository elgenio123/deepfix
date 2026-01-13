import { Button } from "@/components/ui/button";
import { Link } from "wouter";
import { useAuth } from "@/lib/auth";
import { ArrowRight, Code2, Zap, Shield, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";

export default function Landing() {
  const { user } = useAuth();
  const ctaHref = user ? "/dashboard" : "/signup";

  return (
    <div className="flex flex-col min-h-screen bg-background overflow-x-hidden">
      {/* Background Gradients */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 rounded-full blur-[80px] opacity-30 animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/20 rounded-full blur-[80px] opacity-30 animate-pulse delay-1000" />
      </div>

      {/* Hero Section */}
      <section className="relative pt-24 pb-32 md:pt-32 md:pb-40">
        <div className="container px-4 mx-auto text-center max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center rounded-full border px-3 py-1 text-sm font-medium border-primary/20 bg-primary/5 text-primary mb-8 backdrop-blur-sm"
          >
            <span className="relative flex h-2 w-2 mr-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            Now Available for Beta Users
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-5xl md:text-7xl font-bold tracking-tight mb-8"
          >
            Automated Bug Diagnosis for <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-400 to-purple-500 animate-gradient-x">
              Machine Learning Models
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed"
          >
            DeepFix automatically detects bugs, explains root causes, and generates precise fixes—integrated directly into your training pipeline.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-6"
          >
            <Link href={ctaHref}>
              <Button size="lg" className="h-14 px-8 text-lg rounded-full transition-all duration-300 hover:scale-105">
                Get Your API Key <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <a href="https://docs.delcaux.com/" target="_blank" rel="noopener noreferrer">
              <Button variant="outline" size="lg" className="h-14 px-8 text-lg rounded-full border-2 hover:bg-muted/50 transition-all duration-300 hover:scale-105">
                View Documentation
              </Button>
            </a>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 relative">
        <div className="absolute inset-0 bg-muted/40 skew-y-3 transform origin-top-left -z-10" />
        <div className="container px-4 mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Zap className="w-8 h-8 text-yellow-500" />}
              title="Auto-Assessment"
              description="Automatically scan your entire model architecture and dataset for hidden pitfalls, shape mismatches, and numerical instability."
              delay={0}
            />
            <FeatureCard
              icon={<Code2 className="w-8 h-8 text-blue-500" />}
              title="Prioritized Solutions"
              description="Receive actionable fixes ranked by impact. We don't just find the bug; we write the patch code for you."
              delay={0.1}
            />
            <FeatureCard
              icon={<Shield className="w-8 h-8 text-green-500" />}
              title="Workflow Integration"
              description="Seamlessly integrates with PyTorch, TensorFlow, and MLflow. Add one line of code to your existing training script."
              delay={0.2}
            />
          </div>
        </div>
      </section>

      {/* Code Snippet Section */}
      <section className="py-32">
        <div className="container px-4 mx-auto flex flex-col lg:flex-row items-center gap-16">
          <div className="flex-1 space-y-10">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">Simple Python Integration</h2>
              <p className="text-xl text-muted-foreground mb-8">
                DeepFix feels like a native part of your stack. Just initialize the client and let our AI agents analyze your runtime environment.
              </p>
              <ul className="space-y-6">
                {[
                  "Native Python SDK support",
                  "Zero-config PyTorch & TensorFlow hooks",
                  "Automated dataset statistical analysis",
                  "Instant detailed diagnosis reports"
                ].map((item, i) => (
                  <motion.li
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.1 * i, duration: 0.5 }}
                    className="flex items-center gap-4 text-lg"
                  >
                    <div className="rounded-full bg-green-500/10 p-1">
                      <CheckCircle2 className="w-6 h-6 text-green-500" />
                    </div>
                    <span className="font-medium">{item}</span>
                  </motion.li>
                ))}
              </ul>
            </motion.div>
          </div>

          <div className="flex-1 w-full max-w-xl relative">
            <div className="absolute inset-0 bg-gradient-to-r from-primary to-purple-600 rounded-2xl blur-2xl opacity-20 animate-pulse" />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="relative rounded-2xl overflow-hidden shadow-2xl bg-[#0F0F11] border border-white/10"
            >
              <div className="flex items-center gap-2 px-6 py-4 bg-[#18181B] border-b border-white/5">
                <div className="w-3 h-3 rounded-full bg-[#FF5F56]"></div>
                <div className="w-3 h-3 rounded-full bg-[#FFBD2E]"></div>
                <div className="w-3 h-3 rounded-full bg-[#27C93F]"></div>
                <span className="ml-4 text-sm text-gray-400 font-mono">analysis.py</span>
              </div>
              <div className="p-8 overflow-x-auto">
                <pre className="font-mono text-sm text-gray-300 leading-relaxed">
                  <span className="text-purple-400">from</span> deepfix_sdk <span className="text-purple-400">import</span> DeepFixClient{"\n\n"}
                  <span className="text-gray-500"># Initialize client</span>{"\n"}
                  client = DeepFixClient(api_key=<span className="text-green-400">"YOUR_API_KEY"</span>){"\n\n"}
                  <span className="text-gray-500"># Run diagnosis on your datasets</span>{"\n"}
                  result = client.get_diagnosis({"\n"}
                  {"  "}train_data=train_dataset,{"\n"}
                  {"  "}test_data=val_dataset,{"\n"}
                  {"  "}language=<span className="text-green-400">"english"</span>{"\n"}
                  ){"\n\n"}
                  <span className="text-yellow-300">print</span>(result.to_text())
                </pre>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Results Preview Section */}
      <section className="py-24 bg-muted/30">
        <div className="container px-4 mx-auto">
          <div className="text-center mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-4xl md:text-5xl font-bold tracking-tight mb-6"
            >
              Instant, Actionable Reports
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-xl text-muted-foreground max-w-2xl mx-auto"
            >
              Get a full diagnosis with severity ratings, root cause analysis, and ready-to-apply fixes.
            </motion.p>
          </div>

          <div className="max-w-4xl mx-auto space-y-6">
            {/* Summary Card */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="rounded-xl border bg-card p-6 shadow-sm"
            >
              <h3 className="text-lg font-bold text-primary mb-3">Summary</h3>
              <p className="text-muted-foreground leading-relaxed">
                The consolidated analysis reveals a high-quality dataset with minor issues like imbalance, multicollinearity, and outliers that can be addressed through preprocessing (scaling, PCA, transformations) and feature selection to enhance model efficiency. The model configuration is promising with coherent defaults but critically lacks a trained state, reproducibility, and metadata, necessitating immediate training with fixed seeds and class weighting.
              </p>
            </motion.div>

            {/* Summary Statistics Card */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="rounded-xl border bg-card p-6 shadow-sm"
            >
              <h3 className="text-lg font-bold text-primary mb-4">Summary Statistics</h3>
              <div className="flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-8">
                <div className="flex items-center gap-4">
                  <span className="text-muted-foreground">Total Findings</span>
                  <span className="text-2xl font-bold">6</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-muted-foreground">Severity Distribution</span>
                  <div className="flex gap-2">
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-red-500 text-white">HIGH: 2</span>
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-orange-500 text-white">MEDIUM: 3</span>
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-green-500 text-white">LOW: 1</span>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Search & Filter Card */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="rounded-xl border bg-card p-6 shadow-sm"
            >
              <h3 className="text-lg font-bold text-primary mb-4">Search & Filter</h3>
              <div className="flex items-center gap-3 px-4 py-3 rounded-lg border bg-background mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span className="text-muted-foreground">Search findings, evidence, or actions...</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm text-muted-foreground">Filter by severity:</span>
                <div className="flex gap-2">
                  <button className="px-3 py-1 text-sm rounded border border-foreground/20 hover:bg-muted transition-colors">HIGH</button>
                  <button className="px-3 py-1 text-sm rounded border border-foreground/20 hover:bg-muted transition-colors">MEDIUM</button>
                  <button className="px-3 py-1 text-sm rounded border border-foreground/20 hover:bg-muted transition-colors">LOW</button>
                </div>
              </div>
            </motion.div>

            {/* Issues by Severity Card */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="rounded-xl border bg-card p-6 shadow-sm"
            >
              <h3 className="text-lg font-bold text-primary mb-1">Issues by Severity</h3>
              <p className="text-sm text-muted-foreground mb-6">Finding • Evidence • Action • Rationale</p>

              {/* HIGH Severity Accordion */}
              <div className="border rounded-lg overflow-hidden">
                <div className="flex items-center justify-between px-4 py-3 bg-muted/50 cursor-pointer hover:bg-muted transition-colors">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-red-500">HIGH</span>
                    <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-500 text-white">2</span>
                  </div>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                  </svg>
                </div>
                <div className="px-4 py-4 border-t bg-background">
                  <p className="text-foreground leading-relaxed">
                    <span className="font-semibold">1. High multicollinearity (22+ pairs &gt;0.9 correlation)</span> combined with varying feature scales and potential outliers may inflate variance and reduce model stability, especially for tree-based boosting.
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({ icon, title, description, delay }: { icon: React.ReactNode, title: string, description: string, delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      className="group relative p-8 rounded-3xl bg-white/5 border border-white/10 hover:border-primary/50 transition-all duration-300 hover:shadow-2xl hover:shadow-primary/5 hover:-translate-y-1"
    >
      <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-gray-800 to-black border border-white/5 flex items-center justify-center mb-6 shadow-inner group-hover:scale-110 transition-transform duration-300">
        {icon}
      </div>
      <h3 className="text-2xl font-bold mb-4">{title}</h3>
      <p className="text-muted-foreground leading-relaxed text-lg">
        {description}
      </p>
    </motion.div>
  );
}
