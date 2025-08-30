'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b border-gray-100">
      <nav className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">D</span>
            </div>
            <span className="text-xl font-bold text-gray-900">Dictionary App</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/features" className="text-gray-600 hover:text-gray-900 transition">
              Features
            </Link>
            <Link href="/pricing" className="text-gray-600 hover:text-gray-900 transition">
              Pricing
            </Link>
            <Link href="/downloads" className="text-gray-600 hover:text-gray-900 transition">
              Downloads
            </Link>
            <Link href="/docs" className="text-gray-600 hover:text-gray-900 transition">
              Docs
            </Link>
            <Link href="/blog" className="text-gray-600 hover:text-gray-900 transition">
              Blog
            </Link>
            <Link href="/login" className="text-gray-600 hover:text-gray-900 transition">
              Login
            </Link>
            <Link href="/downloads" className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition">
              Download Free
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 pb-4">
            <div className="flex flex-col space-y-4">
              <Link href="/features" className="text-gray-600 hover:text-gray-900 transition">
                Features
              </Link>
              <Link href="/pricing" className="text-gray-600 hover:text-gray-900 transition">
                Pricing
              </Link>
              <Link href="/downloads" className="text-gray-600 hover:text-gray-900 transition">
                Downloads
              </Link>
              <Link href="/docs" className="text-gray-600 hover:text-gray-900 transition">
                Docs
              </Link>
              <Link href="/blog" className="text-gray-600 hover:text-gray-900 transition">
                Blog
              </Link>
              <Link href="/login" className="text-gray-600 hover:text-gray-900 transition">
                Login
              </Link>
              <Link href="/downloads" className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition inline-block text-center">
                Download Free
              </Link>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}