import React, { useState, useEffect } from "react";
import { Zap, MapPin, Clock, AlertCircle, Loader2, CheckCircle2 } from "lucide-react";

const NewIncident = () => {
    const [formData, setFormData] = useState({
        incidentType: "",
        location: "",
        dateTime: new Date().toLocaleString(),
        description: "",
    });

    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    // Update time every second if needed, or just set it once on load
    useEffect(() => {
        const timer = setInterval(() => {
            setFormData((prev) => ({
                ...prev,
                dateTime: new Date().toLocaleString(),
            }));
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!formData.incidentType || !formData.location || !formData.description) {
            alert("Please fill in all fields.");
            return;
        }

        setLoading(true);
        // Simulate AI analysis delay
        setTimeout(() => {
            setLoading(false);
            setSuccess(true);
            setTimeout(() => setSuccess(false), 3000);
        }, 2000);
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div className="text-center space-y-2">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                    Analyze Incoming Incident
                </h2>
                <p className="text-gray-500 dark:text-slate-400">
                    Enter incident details for AI severity prediction
                </p>
            </div>

            {/* Form Card */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-gray-100 dark:border-slate-800 overflow-hidden">
                <form onSubmit={handleSubmit} className="p-8 space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Incident Type */}
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-gray-400 dark:text-slate-500 uppercase tracking-wider flex items-center space-x-2">
                                <AlertCircle size={14} />
                                <span>Incident Type</span>
                            </label>
                            <select
                                name="incidentType"
                                value={formData.incidentType}
                                onChange={handleChange}
                                className="w-full bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl px-4 py-3 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all appearance-none outline-none"
                            >
                                <option value="">Select type...</option>
                                <option value="Fire">Fire / Smoke</option>
                                <option value="Medical">Medical Emergency</option>
                                <option value="Police">Police Requirement</option>
                                <option value="Accident">Road Accident</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>

                        {/* Location */}
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-gray-400 dark:text-slate-500 uppercase tracking-wider flex items-center space-x-2">
                                <MapPin size={14} />
                                <span>Location</span>
                            </label>
                            <input
                                type="text"
                                name="location"
                                placeholder="e.g. Main St & 5th Ave"
                                value={formData.location}
                                onChange={handleChange}
                                className="w-full bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl px-4 py-3 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-600 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                            />
                        </div>
                    </div>

                    {/* Date / Time */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-400 dark:text-slate-500 uppercase tracking-wider flex items-center space-x-2">
                            <Clock size={14} />
                            <span>Date / Time</span>
                        </label>
                        <input
                            type="text"
                            readOnly
                            value={formData.dateTime}
                            className="w-full bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl px-4 py-3 text-gray-400 dark:text-slate-500 cursor-not-allowed outline-none"
                        />
                    </div>

                    {/* Description */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-400 dark:text-slate-500 uppercase tracking-wider flex items-center space-x-2">
                            <span>Description</span>
                        </label>
                        <textarea
                            name="description"
                            rows="4"
                            placeholder="Caller notes: e.g. Smoke visible, smell of gas"
                            value={formData.description}
                            onChange={handleChange}
                            className="w-full bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl px-4 py-3 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-600 focus:ring-2 focus:ring-blue-500 outline-none transition-all resize-none"
                        ></textarea>
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full flex items-center justify-center space-x-3 py-4 rounded-xl font-bold text-lg transition-all transform active:scale-[0.98] ${success
                            ? "bg-green-500 text-white"
                            : "bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white shadow-lg shadow-blue-500/20"
                            } disabled:opacity-70 disabled:cursor-not-allowed`}
                    >
                        {loading ? (
                            <>
                                <Loader2 className="animate-spin" size={24} />
                                <span>AI Analyzing...</span>
                            </>
                        ) : success ? (
                            <>
                                <CheckCircle2 size={24} />
                                <span>Analysis Complete</span>
                            </>
                        ) : (
                            <>
                                <Zap size={20} />
                                <span>Analyze Severity</span>
                            </>
                        )}
                    </button>
                </form>
            </div>

            {/* Info Alert (Optional) */}
            <div className="flex items-start space-x-3 p-4 bg-blue-50/50 dark:bg-blue-900/10 border border-blue-100 dark:border-blue-900/20 rounded-xl">
                <AlertCircle size={20} className="text-blue-500 mt-0.5" />
                <p className="text-sm text-blue-700 dark:text-blue-400">
                    The AI model analyzes time, location, and description to predict the potential severity of the incident. This helps in prioritizing emergency response.
                </p>
            </div>
        </div>
    );
};

export default NewIncident;
