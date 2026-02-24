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
    const [result, setResult] = useState(null);

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

    const handleSubmit = (e) => {
        e.preventDefault();

        const newErrors = {};
        if (!formData.incidentType) newErrors.incidentType = "Please select an incident type";
        if (!formData.location) newErrors.location = "Location is required";
        if (!formData.description) newErrors.description = "Description is required";

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }
        setErrors({});

        setLoading(true);
        setResult(null);

        // 1. Format date and hour for the backend
        const dateObj = new Date(formData.dateTime);
        const dayStr = dateObj.toLocaleDateString('en-US', { weekday: 'short' }); // "Mon", "Tue"

        const requestData = {
            type: formData.incidentType,
            hour: dateObj.getHours(),
            day: dayStr,
            lat: 40.1,  // Hardcoded for now until exact location geocoding is set up
            lng: -75.3
        };

        // 2. Call the Django Backend
        fetch("http://127.0.0.1:8000/api/predictions/predict/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData)
        })
            .then(res => {
                if (!res.ok) {
                    return res.json().then(errData => { throw new Error(errData.error || "Server Error") });
                }
                return res.json();
            })
            .then(data => {
                setLoading(false);
                setSuccess(true);
                setResult({
                    severity: data.severity ? data.severity.toUpperCase() : "UNKNOWN",
                    confidence: data.confidence ? `${(data.confidence * 100).toFixed(0)}%` : "N/A",
                    recommended_response: data.recommended_response || "Determine Response"
                });
            })
            .catch(err => {
                console.error("Prediction failed:", err);
                setLoading(false);
                setErrors({
                    description: `Failed to get prediction from AI server: ${err.message}. Is the backend running?`
                });
            });
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
                                <option value="">-- Select Type --</option>
                                <option value="EMS">EMS</option>
                                <option value="Fire">Fire</option>
                                <option value="Traffic">Traffic</option>
                            </select>
                            {errors.incidentType && <p style={{ color: 'red', fontSize: '12px' }}>{errors.incidentType}</p>}
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
                            {errors.location && <p style={{ color: 'red', fontSize: '12px' }}>{errors.location}</p>}
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
                        {errors.description && <p style={{ color: 'red', fontSize: '12px' }}>{errors.description}</p>}
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={loading || !!result}
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
            {result && (
                <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-gray-100 dark:border-slate-800 overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-500 mt-6">
                    <div className="p-8 space-y-6">
                        <div className="flex items-center justify-between">
                            <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                <Zap className="text-blue-500" size={20} />
                                AI Analysis Result
                            </h3>
                            <span className={`px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-widest border transition-all shadow-sm ${result.severity === 'CRITICAL'
                                ? "bg-red-500 text-white border-red-400 shadow-red-500/20 animate-pulse"
                                : result.severity === 'HIGH'
                                    ? "bg-orange-500 text-white border-orange-400 shadow-orange-500/20"
                                    : "bg-green-500 text-white border-green-400 shadow-green-500/20"
                                }`}>
                                🚨 {result.severity}
                            </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50 transition-all hover:bg-gray-100 dark:hover:bg-slate-800">
                                <p className="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-2">AI Confidence</p>
                                <div className="flex items-end gap-2">
                                    <p className="text-3xl font-black text-blue-600 dark:text-blue-400 tracking-tight">{result.confidence}</p>
                                    <p className="text-xs text-blue-500/60 dark:text-blue-400/60 mb-1 font-bold uppercase">Accuracy</p>
                                </div>
                            </div>
                            <div className="p-5 bg-gray-50 dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700/50 transition-all hover:bg-gray-100 dark:hover:bg-slate-800">
                                <p className="text-[10px] font-black text-gray-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-2">Recommended Response</p>
                                <p className="text-lg font-bold text-gray-900 dark:text-white leading-tight">{result.recommended_response}</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4 pt-2">
                            <button
                                onClick={() => alert('Dispatched!')}
                                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl font-black text-sm uppercase tracking-wider transition-all transform active:scale-[0.98] shadow-lg shadow-blue-500/25 flex items-center justify-center gap-2"
                            >
                                <CheckCircle2 size={18} />
                                Confirm & Dispatch
                            </button>
                            <button
                                onClick={() => {
                                    setResult(null);
                                    setSuccess(false);
                                }}
                                className="px-6 bg-gray-100 dark:bg-slate-800 hover:bg-gray-200 dark:hover:bg-slate-700 text-gray-600 dark:text-slate-300 py-4 rounded-xl font-bold text-sm uppercase tracking-wider transition-all transform active:scale-[0.98] flex items-center justify-center gap-2"
                            >
                                <Zap size={18} className="opacity-50" />
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
