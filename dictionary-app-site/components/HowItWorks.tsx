'use client';

export default function HowItWorks() {
  const steps = [
    {
      number: 1,
      title: 'Select any text',
      description: 'Highlight any word or phrase in any application',
      icon: '🖱️',
    },
    {
      number: 2,
      title: 'Press Ctrl+Ctrl',
      description: 'Double-tap Ctrl (or your custom hotkey)',
      icon: '⌨️',
    },
    {
      number: 3,
      title: 'Get instant definitions',
      description: 'See meanings, examples, and more in a popup',
      icon: '💡',
    },
  ];

  return (
    <section id="how-it-works" className="py-20 px-6 bg-gray-50">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            How It Works
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Three simple steps to instant definitions
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {steps.map((step, index) => (
            <div key={step.number} className="relative">
              <div className="text-center">
                <div className="inline-block mb-4">
                  <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg text-3xl">
                    {step.icon}
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {step.title}
                </h3>
                <p className="text-gray-600">
                  {step.description}
                </p>
              </div>
              
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-10 left-1/2 w-full">
                  <svg className="w-full h-2" viewBox="0 0 100 10">
                    <path
                      d="M 0 5 L 100 5"
                      stroke="#e5e7eb"
                      strokeWidth="2"
                      strokeDasharray="5,5"
                      fill="none"
                    />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Demo Video Placeholder */}
        <div className="mt-16 max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-2xl overflow-hidden">
            <div className="aspect-video bg-gray-200 relative">
              <div className="absolute inset-0 flex items-center justify-center">
                <button className="bg-primary text-white px-8 py-4 rounded-full flex items-center gap-3 hover:bg-primary/90 transition-colors">
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                  </svg>
                  Watch Demo
                </button>
              </div>
              {/* In production, embed actual video or GIF here */}
              <div className="absolute bottom-4 right-4 bg-black/70 text-white px-3 py-1 rounded text-sm">
                0:45
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}