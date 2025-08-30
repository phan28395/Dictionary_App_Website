'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function Hero() {
  const [userOS, setUserOS] = useState<'windows' | 'mac' | 'linux' | 'unknown'>('unknown');

  useEffect(() => {
    const detectOS = () => {
      const userAgent = window.navigator.userAgent.toLowerCase();
      if (userAgent.includes('win')) return 'windows';
      if (userAgent.includes('mac')) return 'mac';
      if (userAgent.includes('linux')) return 'linux';
      return 'unknown';
    };
    setUserOS(detectOS());
  }, []);

  const getDownloadLink = () => {
    switch(userOS) {
      case 'windows': return '/downloads/dictionary-setup.exe';
      case 'mac': return '/downloads/dictionary.dmg';
      case 'linux': return '/downloads/dictionary.AppImage';
      default: return '/downloads';
    }
  };

  const getOSName = () => {
    switch(userOS) {
      case 'windows': return 'for Windows';
      case 'mac': return 'for macOS';
      case 'linux': return 'for Linux';
      default: return '';
    }
  };

  return (
    <section className="pt-32 pb-20 px-6 bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="container mx-auto max-w-6xl">
        <div className="flex flex-col lg:flex-row items-center gap-12">
          {/* Text Content */}
          <div className="flex-1 text-center lg:text-left">
            <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Your Smart <span className="text-primary">Dictionary</span> Companion
            </h1>
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              Instant definitions with a double-tap. Works offline, extends infinitely.
              The dictionary that understands inflected forms like "went" → "go".
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Link 
                href={getDownloadLink()}
                className="bg-primary text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary/90 transition-colors shadow-lg"
              >
                Download Free {getOSName()}
              </Link>
              <button 
                className="bg-white border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-lg text-lg font-semibold hover:border-gray-400 transition-colors"
                onClick={() => {
                  const demoSection = document.getElementById('how-it-works');
                  demoSection?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                View Demo
              </button>
            </div>

            <div className="mt-8 flex flex-wrap gap-6 justify-center lg:justify-start text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>50 free searches</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Works offline</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>No signup required</span>
              </div>
            </div>
          </div>

          {/* Hero Image/Animation */}
          <div className="flex-1">
            <div className="relative">
              <div className="bg-white rounded-2xl shadow-2xl p-8 transform rotate-1 hover:rotate-0 transition-transform duration-300">
                <div className="bg-gray-100 rounded-lg p-6 mb-4">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                  </div>
                  <p className="text-gray-600 mb-2">Select any text and press</p>
                  <div className="flex gap-2 items-center justify-center mb-4">
                    <kbd className="px-3 py-2 bg-white rounded shadow text-sm font-mono">Ctrl</kbd>
                    <span className="text-gray-500">+</span>
                    <kbd className="px-3 py-2 bg-white rounded shadow text-sm font-mono">Ctrl</kbd>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4"></div>
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-5/6"></div>
                </div>
              </div>
              
              {/* Floating badges */}
              <div className="absolute -top-4 -right-4 bg-secondary text-white px-4 py-2 rounded-full text-sm font-semibold shadow-lg">
                Instant Results
              </div>
              <div className="absolute -bottom-4 -left-4 bg-primary text-white px-4 py-2 rounded-full text-sm font-semibold shadow-lg">
                Works Everywhere
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}