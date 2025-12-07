import { Button } from "@/components/ui/button";
import { Link } from "wouter";
import { ArrowRight, Code2, Zap, Shield, CheckCircle2 } from "lucide-react";

export default function Landing() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 md:pt-20 md:pb-28">
        <div className="absolute inset-0 -z-10 opacity-10">
          {/*<img 
            src={heroBg} 
            alt="Background" 
            className="w-full h-full object-cover"
          />*/}
          <div className="absolute inset-0 bg-gradient-to-b from-background via-transparent to-background"></div>
        </div>
        
        <div className="container px-4 mx-auto text-center max-w-5xl">
          <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-primary/10 text-primary hover:bg-primary/20 mb-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
            Now Available for Beta Users
          </div>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-foreground mb-5 animate-in fade-in slide-in-from-bottom-6 duration-700 delay-100">
            Automated Bug Diagnosis for <br/>
            <span className="text-primary">Machine Learning Models</span>
          </h1>
          <p className="text-base md:text-lg text-muted-foreground mb-8 max-w-3xl mx-auto animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200">DeepFix finds what’s broken, explains why, and tells you exactly how to fix it, all automatically, right inside your pipeline.</p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-in fade-in slide-in-from-bottom-10 duration-700 delay-300">
            <Link href="/signup">
              <Button size="lg" className="h-12 px-8 text-base shadow-lg shadow-primary/20">
                Get Your API Key <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
            </Link>
            <a href="https://docs.delcaux.com/" target="_blank" rel="noopener noreferrer">
              <Button variant="outline" size="lg" className="h-12 px-8 text-base">
                View Documentation
              </Button>
            </a>
          </div>
        </div>
      </section>
      {/* Features Section */}
      <section className="py-24 bg-muted/30">
        <div className="container px-4 mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-background p-8 rounded-2xl border shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-6">
                <Zap className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Auto-Assessment</h3>
              <p className="text-muted-foreground leading-relaxed">Automatically scan your models and data for common pitfalls and hidden bugs.</p>
            </div>
            <div className="bg-background p-8 rounded-2xl border shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center mb-6">
                <Code2 className="w-6 h-6 text-accent" />
              </div>
              <h3 className="text-xl font-bold mb-3">Prioritized Solutions</h3>
              <p className="text-muted-foreground leading-relaxed">Get actionable, research-backed recommendations ranked by impact.</p>
            </div>
            <div className="bg-background p-8 rounded-2xl border shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-6">
                <Shield className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">Workflow Integration</h3>
              <p className="text-muted-foreground leading-relaxed">Integrates seamlessly into your existing ML pipelines (PyTorch, scikit-learn, MLflow) with minimal config.</p>
            </div>
          </div>
        </div>
      </section>
      {/* Code Snippet Section */}
      <section className="py-24">
        <div className="container px-4 mx-auto flex flex-col lg:flex-row items-center gap-12">
          <div className="flex-1 space-y-8">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">Simple Python Integration</h2>
            <p className="text-lg text-muted-foreground">
              DeepFix integrates directly into your Python-based ML workflows. Just initialize the client and run a diagnosis on your datasets.
            </p>
            <ul className="space-y-4">
              {[
                "Native Python SDK",
                "Seamless integration with PyTorch & TensorFlow",
                "Automated dataset statistics & checks",
                "Detailed diagnosis reports"
              ].map((item, i) => (
                <li key={i} className="flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                  <span className="font-medium">{item}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="flex-1 w-full max-w-lg">
            <div className="rounded-xl overflow-hidden shadow-2xl bg-[#1e1e1e] border border-gray-800">
              <div className="flex items-center gap-2 px-4 py-3 bg-[#252526] border-b border-gray-800">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <span className="ml-2 text-xs text-gray-400 font-mono">analysis.py</span>
              </div>
              <div className="p-6 overflow-x-auto">
                <pre className="font-mono text-sm text-gray-300 leading-relaxed">
                  <span className="text-purple-400">from</span> deepfix_sdk <span className="text-purple-400">import</span> DeepFixClient<br/><br/>
                  <span className="text-gray-500"># Initialize client</span><br/>
                  client = DeepFixClient(api_key=<span className="text-green-400">"YOUR_API_KEY"</span>)<br/><br/>
                  <span className="text-gray-500"># Run diagnosis on your datasets</span><br/>
                  result = client.get_diagnosis(<br/>
                  &nbsp;&nbsp;train_data=train_dataset,<br/>
                  &nbsp;&nbsp;test_data=val_dataset,<br/>
                  &nbsp;&nbsp;language=<span className="text-green-400">"english"</span><br/>
                  )<br/><br/>
                  <span className="text-yellow-300">print</span>(result.to_text())
                </pre>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
