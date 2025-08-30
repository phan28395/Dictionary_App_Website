'use client';

import { useEffect, useState } from 'react';

interface Testimonial {
  id: string;
  name: string;
  role: string;
  company?: string;
  text: string;
  rating: number;
  avatar: string;
}

const defaultTestimonials: Testimonial[] = [
  {
    id: '1',
    name: 'Sarah Chen',
    role: 'Graduate Student',
    company: 'MIT',
    text: 'The best dictionary app I\'ve ever used! The inflection recognition saves me so much time when reading academic papers.',
    rating: 5,
    avatar: '/images/avatars/sarah.jpg'
  },
  {
    id: '2',
    name: 'Marcus Johnson',
    role: 'Content Writer',
    text: 'As a professional writer, having instant definitions at my fingertips has transformed my workflow. The offline mode is a lifesaver!',
    rating: 5,
    avatar: '/images/avatars/marcus.jpg'
  },
  {
    id: '3',
    name: 'Elena Rodriguez',
    role: 'Language Teacher',
    company: 'International School',
    text: 'My students love it! The extension marketplace lets me customize it perfectly for different language levels.',
    rating: 5,
    avatar: '/images/avatars/elena.jpg'
  }
];

export default function Testimonials() {
  const [testimonials, setTestimonials] = useState<Testimonial[]>(defaultTestimonials);

  useEffect(() => {
    // In production, load from content/testimonials.json
    fetch('/content/testimonials.json')
      .then(res => res.json())
      .then(data => setTestimonials(data.testimonials))
      .catch(() => {
        console.log('Using default testimonials');
      });
  }, []);

  return (
    <section className="py-20 px-6 bg-gray-50">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Loved by Thousands
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            See what our users are saying about Dictionary App
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial) => (
            <div key={testimonial.id} className="bg-white rounded-xl p-6 shadow-lg">
              {/* Rating Stars */}
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <svg
                    key={i}
                    className={`w-5 h-5 ${
                      i < testimonial.rating ? 'text-yellow-400' : 'text-gray-300'
                    }`}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>

              {/* Testimonial Text */}
              <p className="text-gray-600 mb-6 italic">
                "{testimonial.text}"
              </p>

              {/* Author Info */}
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center text-white font-bold">
                  {testimonial.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{testimonial.name}</p>
                  <p className="text-sm text-gray-600">
                    {testimonial.role}
                    {testimonial.company && `, ${testimonial.company}`}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <p className="text-gray-600 mb-4">Join thousands of satisfied users</p>
          <div className="flex justify-center gap-8">
            <div className="text-center">
              <p className="text-3xl font-bold text-gray-900">50K+</p>
              <p className="text-sm text-gray-600">Active Users</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-gray-900">4.8</p>
              <p className="text-sm text-gray-600">Average Rating</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-gray-900">200+</p>
              <p className="text-sm text-gray-600">Extensions</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}