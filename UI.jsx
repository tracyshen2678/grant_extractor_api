import React, { useState } from "react";
import {
  Upload,
  FileText,
  Clock,
  User,
  MapPin,
  Target,
  Users,
  Calendar,
  DollarSign,
  Star,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

const AISpeedReader = () => {
  const [currentView, setCurrentView] = useState("upload"); // 'upload' or 'results'
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [resultData, setResultData] = useState(null); // 存储API返回的真实数据
  const [error, setError] = useState(null); // 错误处理
  const [expandedSections, setExpandedSections] = useState({
    criteria: false,
    synopsis: true,
    keywords: true,
    summary: true,
    score: true,
    evaluation: false,
  });

  // 模拟的API响应数据（仅用于演示，实际使用时删除）
  const mockData = {
    extracted_data: {
      applicant_name: "Matthias Sjöberg",
      applicant_type: "Individual",
      requested_amount: 64000.0,
      project_duration: "2 years",
      work_basis: "full-time",
      project_start_date: {
        year: 2026,
        month: 1,
      },
      project_end_date: {
        year: 2027,
        month: 12,
      },
      main_artistic_field: "Visual Arts - Sculpture",
      main_goal_or_output: "monumental bronze triptych",
      location: "Åbo Skulpturpark",
      target_audience: "Svenskspråkiga skolor och kustsamhällen",
      community_engagement_methods: [
        "Public casting workshops",
        "Oral history interviews",
        "Sketch marathon",
        "Public exhibition",
        "Sculpture workshops in schools",
      ],
      detailed_budget_provided: false,
      co_funding: {
        is_mentioned: true,
        total_amount: 8000.0,
        sources: [
          { source: "Åbo stad", amount: 3000.0 },
          { source: "Konstsamfundet", amount: 5000.0 },
        ],
      },
      partners: [
        "Åbolands Skärgårdsmuseum",
        "Yle Fem",
        "Hufvudstadsbladet",
        "Åbo Akademi",
        "Åbo Konstgjuteri",
      ],
      workspace: "Åbo Konstgjuteri",
      supporting_documents: {
        cv_attached: true,
        portfolio_provided: true,
        portfolio_url: "https://example-artist-site.fi",
        letters_of_intent_attached: false,
        partner_agreements_attached: false,
      },
    },
    synopsis:
      "Matthias Sjöberg planerar att skapa ett monumentalt bronstriptyk som hyllar sydvästra Finlands skärgård, med fokus på att integrera svensk maritim terminologi och miljövänliga tillverkningsmetoder, såsom tångbaserade vaxsläppmedel. Projektet kommer att resultera i en storskalig skulpturserie med taktila punktskriftsskyltar och QR-länkade ljudguider på svenska, vilket främjar tillgänglighet och kulturell respekt. Genom offentliga gjutningsverkstäder och skulpturverkstäder i skolor, syftar projektet till att engagera minst 300 deltagare från svenskspråkiga skolor och kustsamhällen. Dessutom kommer en manual som beskriver projektets tekniker att publiceras öppet, med målet att nå 1 000 nedladdningar inom sex månader.",
    keywords: [
      "konst",
      "brons",
      "skärgård",
      "tillgänglighet",
      "kulturell respekt",
      "offentliga verkstäder",
      "svenskspråkiga skolor",
      "miljövänliga metoder",
      "punktskrift",
      "ljudguider",
    ],
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === "application/pdf") {
      setUploadedFile(file);
      setError(null); // 清除之前的错误
    } else {
      setError("请上传PDF文件");
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type === "application/pdf") {
      setUploadedFile(file);
      setError(null); // 清除之前的错误
    } else {
      setError("请上传PDF文件");
    }
  };

  // 真实的文件上传和处理函数
  const handleProcess = async () => {
    if (!uploadedFile) {
      setError("请先上传PDF文件");
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      // 创建FormData对象来上传文件
      const formData = new FormData();
      formData.append("file", uploadedFile);

      // 调用后端API上传文件并分析 - 修正API路径
      const response = await fetch("/extract/", {
        method: "POST",
        body: formData,
        // 不需要设置Content-Type，浏览器会自动设置multipart/form-data
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `HTTP error! status: ${response.status}`
        );
      }

      const result = await response.json();

      // 存储真实的API响应数据
      setResultData(result);
      setCurrentView("results");
    } catch (error) {
      console.error("文件上传失败:", error);
      setError(error.message || "文件分析失败，请重试");
    } finally {
      setIsProcessing(false);
    }
  };

  // 模拟API调用（仅用于演示，实际使用时删除这个函数）
  const handleProcessDemo = async () => {
    if (!uploadedFile) {
      setError("请先上传PDF文件");
      return;
    }

    setIsProcessing(true);
    setError(null);

    // 模拟API调用延时
    setTimeout(() => {
      setResultData(mockData); // 使用模拟数据
      setIsProcessing(false);
      setCurrentView("results");
    }, 3000);
  };

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("sv-SE", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const resetUpload = () => {
    setUploadedFile(null);
    setError(null);
    setResultData(null);
    setCurrentView("upload");
  };

  if (currentView === "upload") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center mb-4">
              <FileText className="w-12 h-12 text-indigo-600 mr-3" />
              <h1 className="text-3xl font-bold text-gray-800">AI速读工具</h1>
            </div>
            <p className="text-gray-600">智能分析PDF文档，快速提取关键信息</p>
          </div>

          {/* Upload Area */}
          <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
            <div
              className="border-2 border-dashed border-indigo-300 rounded-lg p-12 text-center hover:border-indigo-400 transition-colors cursor-pointer"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => document.getElementById("fileInput").click()}
            >
              <Upload className="w-16 h-16 text-indigo-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-700 mb-2">
                {uploadedFile ? uploadedFile.name : "拖拽PDF文件到这里"}
              </h3>
              <p className="text-gray-500 mb-4">或者点击选择文件</p>
              <input
                id="fileInput"
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                className="hidden"
              />

              {uploadedFile && (
                <div className="mt-4 p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center justify-center text-green-700">
                    <FileText className="w-5 h-5 mr-2" />
                    <span className="font-medium">{uploadedFile.name}</span>
                  </div>
                  <p className="text-sm text-green-600 mt-1">
                    文件大小: {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 rounded-lg border border-red-200">
              <p className="text-red-700 text-center">{error}</p>
            </div>
          )}

          {/* Process Button */}
          <div className="flex gap-4">
            <button
              onClick={handleProcess} // 实际API调用
              disabled={!uploadedFile || isProcessing}
              className={`flex-1 py-4 px-6 rounded-lg font-semibold text-white transition-all ${
                !uploadedFile || isProcessing
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-indigo-600 hover:bg-indigo-700 transform hover:scale-[1.02]"
              }`}
            >
              {isProcessing ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                  正在分析文档...
                </div>
              ) : (
                "开始智能分析"
              )}
            </button>

            <button
              onClick={handleProcessDemo} // 演示模式
              disabled={!uploadedFile || isProcessing}
              className={`flex-1 py-4 px-6 rounded-lg font-semibold text-white transition-all ${
                !uploadedFile || isProcessing
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-green-600 hover:bg-green-700 transform hover:scale-[1.02]"
              }`}
            >
              演示模式
            </button>
          </div>

          {/* Features */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <Clock className="w-8 h-8 text-indigo-600 mb-2" />
              <h4 className="font-semibold text-gray-800">快速分析</h4>
              <p className="text-sm text-gray-600">几秒钟内完成文档分析</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <Target className="w-8 h-8 text-indigo-600 mb-2" />
              <h4 className="font-semibold text-gray-800">精准提取</h4>
              <p className="text-sm text-gray-600">智能识别关键信息</p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <Users className="w-8 h-8 text-indigo-600 mb-2" />
              <h4 className="font-semibold text-gray-800">专业评估</h4>
              <p className="text-sm text-gray-600">AI驱动的内容分析</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Results View
  const data = resultData || mockData; // 使用真实数据或回退到模拟数据

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">分析结果</h1>
              <p className="text-gray-600 mt-1">文档已成功分析并提取关键信息</p>
            </div>
            <button
              onClick={resetUpload}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              上传新文档
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Criteria */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm">
              <div
                className="p-4 border-b cursor-pointer flex items-center justify-between"
                onClick={() => toggleSection("criteria")}
              >
                <div className="flex items-center">
                  <FileText className="w-5 h-5 text-indigo-600 mr-2" />
                  <h3 className="font-semibold text-gray-800">
                    Ursprungliga ansökan
                  </h3>
                </div>
                {expandedSections.criteria ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </div>

              {expandedSections.criteria && (
                <div className="p-4">
                  <div className="space-y-3 text-sm">
                    <p className="font-medium">Rubriken för ansökan</p>
                    <p className="text-gray-600">
                      Lorem ipsum dolor sit amet, consectetur adipiscing elit,
                      sed do eiusmod tempor incididunt ut labore et dolore magna
                      aliqua. Ut enim ad minim veniam, quis nostrud exercitation
                      ullamco laboris nisi ut aliquip ex ea commodo consequat.
                    </p>
                    <p className="text-gray-600">
                      Pellentesque eu erat nisl. Suspendisse lacinia ligula a
                      neque fermentum, sit amet euismod odio placerat. Integer
                      nec rhoncus erat. Duis sed suscipit arcu, id vehicula
                      risus.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* AI-Generated Synopsis */}
            <div className="bg-white rounded-lg shadow-sm">
              <div
                className="p-4 border-b cursor-pointer flex items-center justify-between"
                onClick={() => toggleSection("synopsis")}
              >
                <h3 className="font-semibold text-gray-800">
                  AI-genererad synopsis
                </h3>
                {expandedSections.synopsis ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </div>

              {expandedSections.synopsis && (
                <div className="p-4">
                  <p className="text-gray-700 leading-relaxed">
                    {data.synopsis}
                  </p>
                </div>
              )}
            </div>

            {/* Keywords */}
            <div className="bg-white rounded-lg shadow-sm">
              <div
                className="p-4 border-b cursor-pointer flex items-center justify-between"
                onClick={() => toggleSection("keywords")}
              >
                <h3 className="font-semibold text-gray-800">Keywords</h3>
                {expandedSections.keywords ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </div>

              {expandedSections.keywords && (
                <div className="p-4">
                  <div className="flex flex-wrap gap-2">
                    {data.keywords.map((keyword, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Summary */}
            <div className="bg-white rounded-lg shadow-sm">
              <div
                className="p-4 border-b cursor-pointer flex items-center justify-between"
                onClick={() => toggleSection("summary")}
              >
                <h3 className="font-semibold text-gray-800">Summary</h3>
                {expandedSections.summary ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </div>

              {expandedSections.summary && (
                <div className="p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-4">
                      <div className="flex items-start">
                        <User className="w-5 h-5 text-indigo-600 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium text-gray-800">Namn:</p>
                          <p className="text-gray-600">
                            {data.extracted_data.applicant_name}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-start">
                        <span className="text-indigo-600 mr-2 mt-0.5">💰</span>
                        <div>
                          <p className="font-medium text-gray-800">
                            Ansökt belopp:
                          </p>
                          <p className="text-gray-600">
                            {formatCurrency(
                              data.extracted_data.requested_amount
                            )}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-start">
                        <Calendar className="w-5 h-5 text-indigo-600 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium text-gray-800">
                            Projektets längd:
                          </p>
                          <p className="text-gray-600">
                            {data.extracted_data.project_duration}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-start">
                        <Clock className="w-5 h-5 text-indigo-600 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium text-gray-800">
                            Start- och slutdatum:
                          </p>
                          <p className="text-gray-600">
                            {data.extracted_data.project_start_date.month}/
                            {data.extracted_data.project_start_date.year} -{" "}
                            {data.extracted_data.project_end_date.month}/
                            {data.extracted_data.project_end_date.year}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="flex items-start">
                        <MapPin className="w-5 h-5 text-indigo-600 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium text-gray-800">Plats:</p>
                          <p className="text-gray-600">
                            {data.extracted_data.location}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-start">
                        <Target className="w-5 h-5 text-indigo-600 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium text-gray-800">Målgrupp:</p>
                          <p className="text-gray-600">
                            {data.extracted_data.target_audience}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-start">
                        <Users className="w-5 h-5 text-indigo-600 mr-2 mt-0.5" />
                        <div>
                          <p className="font-medium text-gray-800">
                            Samhällsengagemang:
                          </p>
                          <p className="text-gray-600">
                            {data.extracted_data.community_engagement_methods
                              .slice(0, 2)
                              .join(", ")}
                            ...
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Score */}
            <div className="bg-white rounded-lg shadow-sm">
              <div
                className="p-4 border-b cursor-pointer flex items-center justify-between"
                onClick={() => toggleSection("score")}
              >
                <h3 className="font-semibold text-gray-800">Score</h3>
                {expandedSections.score ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </div>

              {expandedSections.score && (
                <div className="p-4">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-gray-600">
                      Behandlarens poäng av ansökans idé.
                    </span>
                    <span className="text-sm text-gray-500">
                      (1 till 100 poäng)
                    </span>
                  </div>

                  <div className="flex items-center justify-center">
                    <div className="relative">
                      <div className="w-24 h-24 rounded-full bg-gradient-to-r from-orange-400 to-orange-600 flex items-center justify-center">
                        <span className="text-2xl font-bold text-white">
                          50
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* AI Evaluation */}
            <div className="bg-white rounded-lg shadow-sm">
              <div
                className="p-4 border-b cursor-pointer flex items-center justify-between"
                onClick={() => toggleSection("evaluation")}
              >
                <h3 className="font-semibold text-gray-800">AI-evaluation</h3>
                {expandedSections.evaluation ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </div>

              {expandedSections.evaluation && (
                <div className="p-4">
                  <p className="text-gray-600 mb-4">
                    Tycker du att AI-evaluationen föreslog ansökan korrekt?
                  </p>
                  <div className="text-sm text-gray-500 mb-4">
                    (1 till 5 stjärnor)
                  </div>

                  <div className="flex items-center justify-center">
                    <div className="flex space-x-1">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                          key={star}
                          className={`w-8 h-8 cursor-pointer transition-colors ${
                            star <= 4
                              ? "text-yellow-400 fill-current"
                              : "text-gray-300"
                          }`}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AISpeedReader;
