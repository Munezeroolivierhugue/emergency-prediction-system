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
                <p className="text-gray-500 dark:text-neutral-400">
                    Enter incident details for AI severity prediction
                </p>
            </div>

            {/* Form Card */}
            <div className="bg-card rounded-xl border border-border overflow-hidden">
                <form onSubmit={handleSubmit} className="p-8 space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Incident Type */}
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-gray-400 dark:text-neutral-500 uppercase tracking-wider flex items-center space-x-2">
                                <AlertCircle size={14} />
                                <span>Incident Type</span>
                            </label>
                            <select
                                name="incidentType"
                                value={formData.incidentType}
                                onChange={handleChange}
                                className={`w-full bg-background border ${errors.incidentType ? 'border-destructive' : 'border-border'} rounded-lg px-4 py-2.5 text-foreground focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-colors appearance-none`}
                            >
                                <option value="">-- Select Type --</option>
                                <option value="EMS">EMS</option>
                                <option value="Fire">Fire</option>
                                <option value="Traffic">Traffic</option>
                            </select>
                            {errors.incidentType && <p className="text-destructive text-xs">{errors.incidentType}</p>}
                        </div>

                        {/* Location */}
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider flex items-center space-x-2">
                                <MapPin size={14} />
                                <span>Location</span>
                            </label>
                            <input
                                type="text"
                                name="location"
                                placeholder="e.g. Main St & 5th Ave"
                                value={formData.location}
                                onChange={handleChange}
                                className={`w-full bg-background border ${errors.location ? 'border-destructive' : 'border-border'} rounded-lg px-4 py-2.5 text-foreground placeholder:text-muted-foreground focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-colors`}
                            />
                            {errors.location && <p className="text-destructive text-xs">{errors.location}</p>}
                        </div>
                    </div>

                    {/* Date / Time */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-400 dark:text-neutral-500 uppercase tracking-wider flex items-center space-x-2">
                            <Clock size={14} />
                            <span>Date / Time</span>
                        </label>
                        <input
                            type="text"
                            readOnly
                            value={formData.dateTime}
                            className="w-full bg-muted border border-border rounded-lg px-4 py-2.5 text-muted-foreground cursor-not-allowed outline-none"
                        />
                    </div>

                    {/* Description */}
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-gray-400 dark:text-neutral-500 uppercase tracking-wider flex items-center space-x-2">
                            <span>Description</span>
                        </label>
                        <textarea
                            name="description"
                            rows="4"
                            placeholder="Caller notes: e.g. Smoke visible, smell of gas"
                            value={formData.description}
                            onChange={handleChange}
                            className={`w-full bg-background border ${errors.description ? 'border-destructive' : 'border-border'} rounded-lg px-4 py-3 text-foreground placeholder:text-muted-foreground focus:ring-1 focus:ring-primary focus:border-primary outline-none transition-colors resize-none`}
                        ></textarea>
                        {errors.description && <p className="text-destructive text-xs">{errors.description}</p>}
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={loading || !!result}
                        className={`w-full flex items-center justify-center space-x-2 py-3 rounded-lg font-medium transition-colors ${success
                            ? "bg-emerald-600 text-white"
                            : "bg-primary hover:bg-primary/90 text-primary-foreground"
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
                <div className="bg-card rounded-xl border border-border overflow-hidden mt-6">
                    <div className="p-8 space-y-6">
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                                <Zap className="text-primary w-5 h-5" />
                                AI Analysis Result
                            </h3>
                            <span className={`px-3 py-1 rounded-md text-xs font-bold uppercase tracking-wider border ${result.severity === 'CRITICAL'
                                ? "bg-destructive/10 text-destructive border-destructive/20"
                                : result.severity === 'HIGH'
                                    ? "bg-orange-500/10 text-orange-600 border-orange-500/20"
                                    : "bg-emerald-500/10 text-emerald-600 border-emerald-500/20"
                                }`}>
                                {result.severity}
                            </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-4 bg-muted/50 rounded-lg border border-border/50">
                                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">AI Confidence</p>
                                <div className="flex items-end gap-2">
                                    <p className="text-2xl font-bold text-primary">{result.confidence}</p>
                                    <p className="text-xs text-muted-foreground font-medium mb-1">Accuracy</p>
                                </div>
                            </div>
                            <div className="p-4 bg-muted/50 rounded-lg border border-border/50">
                                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Recommended Response</p>
                                <p className="text-base font-semibold text-foreground leading-tight">{result.recommended_response}</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-3 pt-2">
                            <button
                                onClick={() => alert('Dispatched!')}
                                className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground py-2.5 rounded-lg font-medium text-sm transition-colors flex items-center justify-center gap-2"
                            >
                                <CheckCircle2 size={16} />
                                Confirm & Dispatch
                            </button>
                            <button
                                onClick={() => {
                                    setResult(null);
                                    setSuccess(false);
                                }}
                                className="px-6 bg-secondary hover:bg-secondary/80 text-secondary-foreground py-2.5 rounded-lg font-medium text-sm transition-colors flex items-center justify-center gap-2"
                            >
                                <Zap size={16} className="opacity-70" />
                                Ignore
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Info Alert */}
            <div className="flex items-start space-x-3 p-4 bg-muted/30 border border-border rounded-lg mt-6">
                <AlertCircle size={20} className="text-muted-foreground mt-0.5" />
                <p className="text-sm text-foreground">
                    The AI model analyzes time, location, and description to predict the potential severity of the incident. This helps in prioritizing emergency response.
                </p>
            </div>
        </div>
    );
};

export default NewIncident;
