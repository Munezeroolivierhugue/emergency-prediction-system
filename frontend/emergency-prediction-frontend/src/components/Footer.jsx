export default function Footer() {
  return (
    <footer className="bg-gray-50 dark:bg-slate-900 border-t border-gray-200 dark:border-slate-800 py-8 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-500 dark:text-gray-400">
        <p className="mb-2">© {new Date().getFullYear()} Emergency Incident Severity Prediction System.</p>
        <p className="text-sm">Optimizing resource allocation for safer communities.</p>
      </div>
    </footer>
  );
}
