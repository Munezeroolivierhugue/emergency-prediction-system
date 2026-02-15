export default function Dashboard() {
  return (
    <div className="min-h-screen bg-[#F4F6F8] dark:bg-[#0F172A] text-[#1A1A1A] dark:text-[#F1F5F9] p-6">
      
      <div className="bg-white dark:bg-[#1E293B] p-6 rounded-2xl shadow">
        <h1 className="text-2xl font-bold text-[#E53935]">
          Emergency Dashboard
        </h1>
        <p className="text-gray-500 dark:text-slate-400">
          Real-time incident monitoring
        </p>
      </div>

      <button className="mt-6 bg-[#E53935] hover:bg-red-700 text-white px-6 py-3 rounded-xl">
        Trigger Alert
      </button>

    </div>
  );
}
