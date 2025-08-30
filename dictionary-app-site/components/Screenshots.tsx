'use client';

import { useState } from 'react';
import Image from 'next/image';

export default function Screenshots() {
  const screenshots = [
    {
      id: 'popup',
      title: 'Dictionary Popup',
      description: 'Clean, instant definitions',
      image: '/images/screenshots/popup.png',
    },
    {
      id: 'search',
      title: 'Search Results',
      description: 'Multiple meanings with examples',
      image: '/images/screenshots/search.png',
    },
    {
      id: 'settings',
      title: 'Settings Panel',
      description: 'Customize everything',
      image: '/images/screenshots/settings.png',
    },
    {
      id: 'extensions',
      title: 'Extension Store',
      description: 'Browse and install extensions',
      image: '/images/screenshots/extensions.png',
    },
    {
      id: 'dark-mode',
      title: 'Dark Mode',
      description: 'Easy on the eyes',
      image: '/images/screenshots/dark-mode.png',
    },
    {
      id: 'multi-platform',
      title: 'Cross Platform',
      description: 'Works on all major OS',
      image: '/images/screenshots/platforms.png',
    },
  ];

  const [selectedImage, setSelectedImage] = useState(0);

  return (
    <section className="py-20 px-6 bg-white">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            See It in Action
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Beautiful, functional, and fast on every platform
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Main Screenshot Display */}
          <div className="order-2 lg:order-1">
            <div className="bg-gray-100 rounded-xl p-4 shadow-xl">
              <div className="bg-white rounded-lg overflow-hidden">
                {/* Placeholder for actual screenshot */}
                <div className="aspect-video bg-gradient-to-br from-blue-100 to-green-100 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-6xl mb-4">📸</div>
                    <p className="text-gray-600 font-semibold">{screenshots[selectedImage].title}</p>
                    <p className="text-gray-500 text-sm mt-2">{screenshots[selectedImage].description}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Screenshot Thumbnails */}
          <div className="order-1 lg:order-2">
            <div className="grid grid-cols-2 gap-4">
              {screenshots.map((screenshot, index) => (
                <button
                  key={screenshot.id}
                  onClick={() => setSelectedImage(index)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedImage === index
                      ? 'border-primary bg-primary/5'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-left">
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {screenshot.title}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {screenshot.description}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Platform badges */}
        <div className="mt-16 flex flex-wrap justify-center gap-8">
          <div className="flex items-center gap-2 text-gray-600">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M3 5.109C3 4.496 3.47 4 4.05 4h8.1c.58 0 1.05.496 1.05 1.109V6.5h7.35c.58 0 1.05.496 1.05 1.109V19.39c0 .614-.47 1.11-1.05 1.11H3.45c-.58 0-1.05-.496-1.05-1.109V5.109zm8.85 9.141h-7.7v4.64h7.7v-4.64zm0-1.5v-4.64h-7.7v4.64h7.7zm1.5 1.5v4.64h7.7v-4.64h-7.7zm7.7-1.5v-4.64h-7.7v4.64h7.7z"/>
            </svg>
            <span>Windows 10/11</span>
          </div>
          <div className="flex items-center gap-2 text-gray-600">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
            </svg>
            <span>macOS 11+</span>
          </div>
          <div className="flex items-center gap-2 text-gray-600">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            <span>Linux</span>
          </div>
        </div>
      </div>
    </section>
  );
}