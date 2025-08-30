'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Feature {
  id: string;
  icon: string;
  title: string;
  description: string;
  details?: string;
}

const defaultFeatures: Feature[] = [
  {
    id: 'smart-search',
    icon: '🔍',
    title: 'Smart Search',
    description: 'Handles inflected forms like "went" → "go" automatically',
    details: 'Our advanced linguistic engine understands word variations, plurals, past tenses, and conjugations across multiple languages.'
  },
  {
    id: 'offline',
    icon: '📡',
    title: 'Works Offline',
    description: 'Full functionality without internet connection',
    details: 'Download once and use forever. All definitions, examples, and features work completely offline.'
  },
  {
    id: 'fast',
    icon: '⚡',
    title: 'Lightning Fast',
    description: 'Get definitions in milliseconds, not seconds',
    details: 'Optimized database and smart caching means instant results every time.'
  },
  {
    id: 'extensions',
    icon: '🧩',
    title: 'Extension Marketplace',
    description: 'Customize with themes, language packs, and tools',
    details: 'Browse hundreds of extensions to personalize your dictionary experience.'
  },
  {
    id: 'global-hotkey',
    icon: '⌨️',
    title: 'Global Hotkey',
    description: 'Double-tap Ctrl to search selected text anywhere',
    details: 'Works in any application - browsers, documents, emails, anywhere you can select text.'
  },
  {
    id: 'privacy',
    icon: '🔒',
    title: 'Privacy First',
    description: 'Your searches stay on your device',
    details: 'No tracking, no ads, no data collection. Your vocabulary is your business.'
  }
];

export default function Features() {
  const [features, setFeatures] = useState<Feature[]>(defaultFeatures);
  const [expandedFeature, setExpandedFeature] = useState<string | null>(null);

  useEffect(() => {
    // In production, load from content/features.json
    fetch('/content/features.json')
      .then(res => res.json())
      .then(data => setFeatures(data.features))
      .catch(() => {
        // Use default features if file doesn't exist
        console.log('Using default features');
      });
  }, []);

  return (
    <section id="features" className="py-20 px-6 bg-white">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Powerful Features for Everyone
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            From students to professionals, our dictionary adapts to your needs
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature) => (
            <div 
              key={feature.id}
              className="group relative bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer"
              onClick={() => setExpandedFeature(expandedFeature === feature.id ? null : feature.id)}
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 mb-4">
                {feature.description}
              </p>
              
              {expandedFeature === feature.id && feature.details && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm text-gray-600">{feature.details}</p>
                </div>
              )}
              
              <div className="absolute bottom-4 right-4 text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <Link href="/features" className="inline-flex items-center gap-2 text-primary hover:text-primary/80 font-semibold">
            Explore all features
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </Link>
        </div>
      </div>
    </section>
  );
}