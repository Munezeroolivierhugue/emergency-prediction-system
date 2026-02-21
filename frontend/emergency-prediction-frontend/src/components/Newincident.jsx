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
    const [errors, setErrors] = useState({});
    const [analysisResult, setAnalysisResult] = useState(null);

    // Update time every second
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
        // Clear error when user starts typing
        if (errors[name]) {
            setErrors((prev) => ({ ...prev, [name]: "" }));
        }
    };

    const validateForm = () => {
        const newErrors = {};
        if (!formData.incidentType) newErrors.incidentType = "Incident type is required";
        if (!formData.location) newErrors.location = "Location is required";
        if (!formData.description) newErrors.description = "Description is required";
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        setLoading(true);
        setAnalysisResult(null);

        // Simulate AI analysis delay
        setTimeout(() => {
            setLoading(false);
            setSuccess(true);
            setAnalysisResult({
                severity: "CRITICAL",
                confidence: 94,
                recommendation: "Dispatch 3 Units"
            });
        }, 2000);
    };

    const handleReset = () => {
        setFormData({
            incidentType: "",
            location: "",
            dateTime: new Date().toLocaleString(),
            description: "",
        });
        setSuccess(false);
        setAnalysisResult(null);
        setErrors({});
    };

    const getSeverityStyles = (severity) => {
        switch (severity) {
            case "CRITICAL": return "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400 border-red-200 dark:border-red-900";
            case "HIGH": return "bg-orange-100 text-orange-700 dark:bg-orange-500/10 dark:text-orange-400 border-orange-200 dark:border-orange-900";
            case "LOW": return "bg-green-100 text-green-700 dark:bg-green-500/10 dark:text-green-400 border-green-200 dark:border-green-900";
            default: return "bg-gray-100 text-gray-700 dark:bg-slate-800 dark:text-slate-400 border-gray-200 dark:border-slate-700";
        }
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
                                className={`w-full bg-gray-50 dark:bg-slate-800 border ${errors.incidentType ? 'border-red-500' : 'border-gray-200 dark:border-slate-700'} rounded-xl px-4 py-3 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all appearance-none`}
                            >
                                <option value="">Select type...</option>
                                <option value="Fire">Fire / Smoke</option>
                                <option value="Medical">Medical Emergency</option>
                                <option value="Rescue">Rescue</option>
                                <option value="Traffic">Traffic</option>
                                <option value="Other">Other</option>
                            </select>
                            {errors.incidentType && <p className="text-red-500 text-xs mt-1">{errors.incidentType}</p>}
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
                                className={`w-full bg-gray-50 dark:bg-slate-800 border ${errors.location ? 'border-red-500' : 'border-gray-200 dark:border-slate-700'} rounded-xl px-4 py-3 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-600 focus:ring-2 focus:ring-blue-500 outline-none transition-all`}
                            />
                            {errors.location && <p className="text-red-500 text-xs mt-1">{errors.location}</p>}
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
                            className={`w-full bg-gray-50 dark:bg-slate-800 border ${errors.description ? 'border-red-500' : 'border-gray-200 dark:border-slate-700'} rounded-xl px-4 py-3 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-600 focus:ring-2 focus:ring-blue-500 outline-none transition-all resize-none`}
                        ></textarea>
                        {errors.description && <p className="text-red-500 text-xs mt-1">{errors.description}</p>}
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={loading || !!analysisResult}
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

            {/* Analysis Result Panel */}
            {analysisResult && (
                <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-gray-100 dark:border-slate-800 overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-500">
                    <div className="p-8 space-y-6">
                        <div className="flex items-center justify-between">
                            <h3 className="text-xl font-bold text-gray-900 dark:text-white">AI Analysis Result</h3>
                            <span className={`px-4 py-1.5 rounded-full text-sm font-bold border ${getSeverityStyles(analysisResult.severity)}`}>
                                {analysisResult.severity}
                            </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="p-4 bg-gray-50 dark:bg-slate-800 rounded-xl border border-gray-100 dark:border-slate-700">
                                <p className="text-xs font-bold text-gray-400 dark:text-slate-500 uppercase tracking-wider mb-1">AI Confidence Score</p>
                                <p className="text-2xl font-black text-blue-600 dark:text-blue-400">{analysisResult.confidence}%</p>
                            </div>
                            <div className="p-4 bg-gray-50 dark:bg-slate-800 rounded-xl border border-gray-100 dark:border-slate-800">
                                <p className="text-xs font-bold text-gray-400 dark:text-slate-500 uppercase tracking-wider mb-1">Recommended Response</p>
                                <p className="text-lg font-bold text-gray-900 dark:text-white">{analysisResult.recommendation}</p>
                            </div>
                        </div>

                        <div className="flex grid-cols-2 gap-4">
                            <button
                                onClick={() => alert("Dispatching units...")}
                                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl font-bold transition-colors"
                            >
                                Confirm & Dispatch
                            </button>
                            <button
                                onClick={handleReset}
                                className="flex-1 bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 text-gray-600 dark:text-slate-300 py-3 rounded-xl font-bold transition-colors"
                            >
                                Ignore
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Info Alert */}
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
