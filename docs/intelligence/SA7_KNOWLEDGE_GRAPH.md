# SA-7: Knowledge Graph

## Route Index
| Route | File | Handler | DB / External Touchpoints |
| --- | --- | --- | --- |
| POST /auth/register | voice_agent_backend/app/api/routes/auth.py:20 | register | see backend/data/integration reports |
| POST /auth/login | voice_agent_backend/app/api/routes/auth.py:39 | login | see backend/data/integration reports |
| POST /chat | voice_agent_backend/app/api/routes/chat.py:52 | chat_endpoint | see backend/data/integration reports |
| POST /chat/predict | voice_agent_backend/app/api/routes/chat.py:291 | chat_predict_endpoint | see backend/data/integration reports |
| POST /chat/backchannel/{session_id} | voice_agent_backend/app/api/routes/chat.py:328 | chat_backchannel_endpoint | see backend/data/integration reports |
| POST /chat/stream | voice_agent_backend/app/api/routes/chat.py:353 | chat_stream_endpoint | see backend/data/integration reports |
| POST /chat/interrupt/{thread_id} | voice_agent_backend/app/api/routes/chat.py:488 | interrupt_endpoint | see backend/data/integration reports |
| GET /collections | voice_agent_backend/app/api/routes/collections.py:15 | get_collections | see backend/data/integration reports |
| POST /collections | voice_agent_backend/app/api/routes/collections.py:25 | create_collection_endpoint | see backend/data/integration reports |
| DELETE /collections/{collection_name} | voice_agent_backend/app/api/routes/collections.py:39 | delete_collection_endpoint | see backend/data/integration reports |
| GET /collections/{collection_name}/documents | voice_agent_backend/app/api/routes/collections.py:51 | get_documents | see backend/data/integration reports |
| DELETE /collections/{collection_name}/documents/{filename} | voice_agent_backend/app/api/routes/collections.py:61 | delete_document | see backend/data/integration reports |
| GET /health | voice_agent_backend/app/api/routes/health.py:10 | health | see backend/data/integration reports |
| POST /ingest | voice_agent_backend/app/api/routes/ingest.py:396 | ingest_endpoint | see backend/data/integration reports |
| GET /models | voice_agent_backend/app/api/routes/models.py:34 | list_available_models | see backend/data/integration reports |
| POST /stt | voice_agent_backend/app/api/routes/stt.py:8 | speech_to_text | see backend/data/integration reports |
| POST /tts/generate | voice_agent_backend/app/api/routes/tts.py:17 | generate_tts | see backend/data/integration reports |

## Function Index
| Function | File:Line | Kind | Purpose |
| --- | --- | --- | --- |
| rel | docs/intelligence/_generate_docs.py:25 | sync | inferred from module/name; inspect source for exact body |
| ignored | docs/intelligence/_generate_docs.py:29 | sync | inferred from module/name; inspect source for exact body |
| is_binary | docs/intelligence/_generate_docs.py:39 | sync | inferred from module/name; inspect source for exact body |
| is_text | docs/intelligence/_generate_docs.py:43 | sync | inferred from module/name; inspect source for exact body |
| read | docs/intelligence/_generate_docs.py:47 | sync | inferred from module/name; inspect source for exact body |
| ref | docs/intelligence/_generate_docs.py:53 | sync | inferred from module/name; inspect source for exact body |
| cmd | docs/intelligence/_generate_docs.py:57 | sync | inferred from module/name; inspect source for exact body |
| table | docs/intelligence/_generate_docs.py:65 | sync | inferred from module/name; inspect source for exact body |
| block | docs/intelligence/_generate_docs.py:72 | sync | inferred from module/name; inspect source for exact body |
| write | docs/intelligence/_generate_docs.py:76 | sync | inferred from module/name; inspect source for exact body |
| pad | docs/intelligence/_generate_docs.py:82 | sync | inferred from module/name; inspect source for exact body |
| register | voice_agent_backend/app/api/routes/auth.py:21 | async | inferred from module/name; inspect source for exact body |
| login | voice_agent_backend/app/api/routes/auth.py:40 | async | inferred from module/name; inspect source for exact body |
| chat_endpoint | voice_agent_backend/app/api/routes/chat.py:54 | async | inferred from module/name; inspect source for exact body |
| blocked_generate | voice_agent_backend/app/api/routes/chat.py:81 | async | inferred from module/name; inspect source for exact body |
| generate | voice_agent_backend/app/api/routes/chat.py:134 | async | inferred from module/name; inspect source for exact body |
| chat_predict_endpoint | voice_agent_backend/app/api/routes/chat.py:292 | async | inferred from module/name; inspect source for exact body |
| chat_backchannel_endpoint | voice_agent_backend/app/api/routes/chat.py:329 | async | inferred from module/name; inspect source for exact body |
| chat_stream_endpoint | voice_agent_backend/app/api/routes/chat.py:355 | async | inferred from module/name; inspect source for exact body |
| side_car_backchannel_listener | voice_agent_backend/app/api/routes/chat.py:415 | async | inferred from module/name; inspect source for exact body |
| stream_graph | voice_agent_backend/app/api/routes/chat.py:434 | async | inferred from module/name; inspect source for exact body |
| run_graph | voice_agent_backend/app/api/routes/chat.py:443 | async | inferred from module/name; inspect source for exact body |
| interrupt_endpoint | voice_agent_backend/app/api/routes/chat.py:490 | async | inferred from module/name; inspect source for exact body |
| stream_resume | voice_agent_backend/app/api/routes/chat.py:509 | async | inferred from module/name; inspect source for exact body |
| get_collections | voice_agent_backend/app/api/routes/collections.py:16 | async | inferred from module/name; inspect source for exact body |
| create_collection_endpoint | voice_agent_backend/app/api/routes/collections.py:26 | async | inferred from module/name; inspect source for exact body |
| delete_collection_endpoint | voice_agent_backend/app/api/routes/collections.py:40 | async | inferred from module/name; inspect source for exact body |
| get_documents | voice_agent_backend/app/api/routes/collections.py:52 | async | inferred from module/name; inspect source for exact body |
| delete_document | voice_agent_backend/app/api/routes/collections.py:62 | async | inferred from module/name; inspect source for exact body |
| health | voice_agent_backend/app/api/routes/health.py:11 | async | inferred from module/name; inspect source for exact body |
| is_heading_line | voice_agent_backend/app/api/routes/ingest.py:48 | sync | inferred from module/name; inspect source for exact body |
| is_table_line | voice_agent_backend/app/api/routes/ingest.py:68 | sync | inferred from module/name; inspect source for exact body |
| chunk_text_simple | voice_agent_backend/app/api/routes/ingest.py:79 | sync | inferred from module/name; inspect source for exact body |
| recursive_split_inner | voice_agent_backend/app/api/routes/ingest.py:83 | sync | inferred from module/name; inspect source for exact body |
| chunk_structured_lines | voice_agent_backend/app/api/routes/ingest.py:129 | sync | inferred from module/name; inspect source for exact body |
| flush_block | voice_agent_backend/app/api/routes/ingest.py:144 | sync | inferred from module/name; inspect source for exact body |
| extract_text_from_pdf | voice_agent_backend/app/api/routes/ingest.py:227 | sync | inferred from module/name; inspect source for exact body |
| extract_text_from_docx | voice_agent_backend/app/api/routes/ingest.py:251 | sync | inferred from module/name; inspect source for exact body |
| extract_text_from_txt | voice_agent_backend/app/api/routes/ingest.py:267 | sync | inferred from module/name; inspect source for exact body |
| ingest_document | voice_agent_backend/app/api/routes/ingest.py:274 | async | inferred from module/name; inspect source for exact body |
| ingest_endpoint | voice_agent_backend/app/api/routes/ingest.py:398 | async | inferred from module/name; inspect source for exact body |
| _kokoro_gpu_usable | voice_agent_backend/app/api/routes/models.py:11 | sync | inferred from module/name; inspect source for exact body |
| list_available_models | voice_agent_backend/app/api/routes/models.py:35 | async | inferred from module/name; inspect source for exact body |
| speech_to_text | voice_agent_backend/app/api/routes/stt.py:9 | async | inferred from module/name; inspect source for exact body |
| generate_tts | voice_agent_backend/app/api/routes/tts.py:18 | async | inferred from module/name; inspect source for exact body |
| audio_stream | voice_agent_backend/app/api/routes/tts.py:19 | async | inferred from module/name; inspect source for exact body |
| supervisor_node | voice_agent_backend/app/core/agents/supervisor.py:12 | async | inferred from module/name; inspect source for exact body |
| route_after_supervisor | voice_agent_backend/app/core/agents/supervisor.py:56 | sync | inferred from module/name; inspect source for exact body |
| ultrathink_critic_node | voice_agent_backend/app/core/agents/ultrathink_critic.py:15 | async | inferred from module/name; inspect source for exact body |
| verify_password | voice_agent_backend/app/core/auth.py:17 | sync | inferred from module/name; inspect source for exact body |
| get_password_hash | voice_agent_backend/app/core/auth.py:21 | sync | inferred from module/name; inspect source for exact body |
| create_access_token | voice_agent_backend/app/core/auth.py:25 | sync | inferred from module/name; inspect source for exact body |
| get_current_user | voice_agent_backend/app/core/auth.py:40 | async | inferred from module/name; inspect source for exact body |
| get_embed_dim | voice_agent_backend/app/core/config.py:47 | sync | inferred from module/name; inspect source for exact body |
| validate_secret_key | voice_agent_backend/app/core/config.py:132 | sync | inferred from module/name; inspect source for exact body |
| resolve_project_relative_path | voice_agent_backend/app/core/config.py:139 | sync | inferred from module/name; inspect source for exact body |
| correlate_query | voice_agent_backend/app/core/correlator.py:24 | async | inferred from module/name; inspect source for exact body |
| get_db | voice_agent_backend/app/core/database.py:17 | async | inferred from module/name; inspect source for exact body |
| init_db | voice_agent_backend/app/core/database.py:21 | async | inferred from module/name; inspect source for exact body |
| map_slang_to_formal | voice_agent_backend/app/core/intent.py:117 | sync | inferred from module/name; inspect source for exact body |
| detect_prompt_injection | voice_agent_backend/app/core/intent.py:125 | sync | inferred from module/name; inspect source for exact body |
| is_follow_up_query | voice_agent_backend/app/core/intent.py:131 | sync | inferred from module/name; inspect source for exact body |
| classify_intent_fast | voice_agent_backend/app/core/intent.py:143 | sync | inferred from module/name; inspect source for exact body |
| classify_intent_llm | voice_agent_backend/app/core/intent.py:203 | async | inferred from module/name; inspect source for exact body |
| classify_intent | voice_agent_backend/app/core/intent.py:229 | async | inferred from module/name; inspect source for exact body |
| tokenize | voice_agent_backend/app/core/langchain_rag.py:37 | sync | inferred from module/name; inspect source for exact body |
| build_query_variants | voice_agent_backend/app/core/langchain_rag.py:43 | sync | inferred from module/name; inspect source for exact body |
| rerank_results | voice_agent_backend/app/core/langchain_rag.py:93 | sync | inferred from module/name; inspect source for exact body |
| diversify_for_summary | voice_agent_backend/app/core/langchain_rag.py:177 | sync | inferred from module/name; inspect source for exact body |
| has_sufficient_confidence | voice_agent_backend/app/core/langchain_rag.py:198 | sync | inferred from module/name; inspect source for exact body |
| format_context | voice_agent_backend/app/core/langchain_rag.py:210 | sync | inferred from module/name; inspect source for exact body |
| build_contextual_prompt | voice_agent_backend/app/core/langchain_rag.py:247 | sync | inferred from module/name; inspect source for exact body |
| retrieve_context | voice_agent_backend/app/core/langchain_rag.py:295 | async | inferred from module/name; inspect source for exact body |
| __init__ | voice_agent_backend/app/core/memory.py:12 | sync | inferred from module/name; inspect source for exact body |
| get_or_create | voice_agent_backend/app/core/memory.py:17 | sync | inferred from module/name; inspect source for exact body |
| append_turn | voice_agent_backend/app/core/memory.py:30 | sync | inferred from module/name; inspect source for exact body |
| get_history | voice_agent_backend/app/core/memory.py:41 | sync | inferred from module/name; inspect source for exact body |
| set_last_retrieval | voice_agent_backend/app/core/memory.py:44 | sync | inferred from module/name; inspect source for exact body |
| get_last_retrieval | voice_agent_backend/app/core/memory.py:49 | sync | inferred from module/name; inspect source for exact body |
| clear | voice_agent_backend/app/core/memory.py:52 | sync | inferred from module/name; inspect source for exact body |
| set_language | voice_agent_backend/app/core/memory.py:56 | sync | inferred from module/name; inspect source for exact body |
| get_language | voice_agent_backend/app/core/memory.py:61 | sync | inferred from module/name; inspect source for exact body |
| set_active_collection | voice_agent_backend/app/core/memory.py:64 | sync | inferred from module/name; inspect source for exact body |
| get_active_collection | voice_agent_backend/app/core/memory.py:69 | sync | inferred from module/name; inspect source for exact body |
| check_confidence_node | voice_agent_backend/app/core/nodes/check_confidence.py:16 | sync | inferred from module/name; inspect source for exact body |
| route_after_confidence | voice_agent_backend/app/core/nodes/check_confidence.py:55 | sync | inferred from module/name; inspect source for exact body |
| check_interrupt_node | voice_agent_backend/app/core/nodes/check_interrupt.py:15 | sync | inferred from module/name; inspect source for exact body |
| route_after_interrupt | voice_agent_backend/app/core/nodes/check_interrupt.py:48 | sync | inferred from module/name; inspect source for exact body |
| classify_intent_node | voice_agent_backend/app/core/nodes/classify_intent.py:17 | async | inferred from module/name; inspect source for exact body |
| route_after_classify | voice_agent_backend/app/core/nodes/classify_intent.py:56 | sync | inferred from module/name; inspect source for exact body |
| _extract_ready_tts_chunks | voice_agent_backend/app/core/nodes/generate_response.py:21 | sync | inferred from module/name; inspect source for exact body |
| generate_response_node | voice_agent_backend/app/core/nodes/generate_response.py:79 | async | inferred from module/name; inspect source for exact body |
| tts_worker | voice_agent_backend/app/core/nodes/generate_response.py:157 | async | inferred from module/name; inspect source for exact body |
| handle_early_exit_node | voice_agent_backend/app/core/nodes/handle_early_exit.py:44 | async | inferred from module/name; inspect source for exact body |
| retrieve_context_node | voice_agent_backend/app/core/nodes/retrieve_context.py:15 | async | inferred from module/name; inspect source for exact body |
| search_web_node | voice_agent_backend/app/core/nodes/search_web.py:16 | async | inferred from module/name; inspect source for exact body |
| synthesize_speech_node | voice_agent_backend/app/core/nodes/synthesize_speech.py:16 | async | inferred from module/name; inspect source for exact body |
| translate_input_node | voice_agent_backend/app/core/nodes/translate_input.py:16 | async | inferred from module/name; inspect source for exact body |
| update_context_node | voice_agent_backend/app/core/nodes/update_context.py:20 | async | inferred from module/name; inspect source for exact body |
| configure_onnxruntime_gpu_environment | voice_agent_backend/app/core/onnx_runtime.py:8 | sync | inferred from module/name; inspect source for exact body |
| translate_to_english | voice_agent_backend/app/core/translation.py:5 | async | inferred from module/name; inspect source for exact body |
| translate_from_english | voice_agent_backend/app/core/translation.py:31 | async | inferred from module/name; inspect source for exact body |
| build_voice_graph | voice_agent_backend/app/core/voice_graph.py:35 | sync | inferred from module/name; inspect source for exact body |
| get_compiled_graph | voice_agent_backend/app/core/voice_graph.py:129 | sync | inferred from module/name; inspect source for exact body |
| __getattr__ | voice_agent_backend/app/core/voice_graph.py:139 | sync | inferred from module/name; inspect source for exact body |
| __call__ | voice_agent_backend/app/core/voice_graph.py:142 | sync | inferred from module/name; inspect source for exact body |
| dispatch | voice_agent_backend/app/main.py:25 | async | inferred from module/name; inspect source for exact body |
| startup_event | voice_agent_backend/app/main.py:47 | async | inferred from module/name; inspect source for exact body |
| warm_tts | voice_agent_backend/app/main.py:57 | async | inferred from module/name; inspect source for exact body |
| shutdown_event | voice_agent_backend/app/main.py:75 | async | inferred from module/name; inspect source for exact body |
| global_exception_handler | voice_agent_backend/app/main.py:81 | async | inferred from module/name; inspect source for exact body |
| dispatch | voice_agent_backend/app/middleware/logging.py:10 | async | inferred from module/name; inspect source for exact body |
| chat_complete | voice_agent_backend/app/services/groq_service.py:9 | sync | inferred from module/name; inspect source for exact body |
| _stream_chat | voice_agent_backend/app/services/groq_service.py:44 | async | inferred from module/name; inspect source for exact body |
| _non_stream_chat | voice_agent_backend/app/services/groq_service.py:68 | async | inferred from module/name; inspect source for exact body |
| transcribe_audio | voice_agent_backend/app/services/groq_service.py:80 | async | inferred from module/name; inspect source for exact body |
| health_check | voice_agent_backend/app/services/groq_service.py:121 | async | inferred from module/name; inspect source for exact body |
| list_models | voice_agent_backend/app/services/groq_service.py:136 | async | inferred from module/name; inspect source for exact body |
| get_client | voice_agent_backend/app/services/http_client.py:14 | async | inferred from module/name; inspect source for exact body |
| close | voice_agent_backend/app/services/http_client.py:25 | async | inferred from module/name; inspect source for exact body |
| get_http_client | voice_agent_backend/app/services/http_client.py:31 | async | inferred from module/name; inspect source for exact body |
| chat_complete | voice_agent_backend/app/services/llm_router.py:4 | sync | inferred from module/name; inspect source for exact body |
| generate_embedding | voice_agent_backend/app/services/ollama_service.py:9 | async | inferred from module/name; inspect source for exact body |
| chat_complete | voice_agent_backend/app/services/ollama_service.py:50 | sync | inferred from module/name; inspect source for exact body |
| _stream_chat | voice_agent_backend/app/services/ollama_service.py:75 | async | inferred from module/name; inspect source for exact body |
| _non_stream_chat | voice_agent_backend/app/services/ollama_service.py:97 | async | inferred from module/name; inspect source for exact body |
| list_models | voice_agent_backend/app/services/ollama_service.py:107 | async | inferred from module/name; inspect source for exact body |
| health_check | voice_agent_backend/app/services/ollama_service.py:120 | async | inferred from module/name; inspect source for exact body |
| _qdrant_get | voice_agent_backend/app/services/qdrant_service.py:13 | async | inferred from module/name; inspect source for exact body |
| _qdrant_post | voice_agent_backend/app/services/qdrant_service.py:28 | async | inferred from module/name; inspect source for exact body |
| _qdrant_put | voice_agent_backend/app/services/qdrant_service.py:43 | async | inferred from module/name; inspect source for exact body |
| _qdrant_delete | voice_agent_backend/app/services/qdrant_service.py:58 | async | inferred from module/name; inspect source for exact body |
| list_collections | voice_agent_backend/app/services/qdrant_service.py:76 | async | inferred from module/name; inspect source for exact body |
| create_collection | voice_agent_backend/app/services/qdrant_service.py:82 | async | inferred from module/name; inspect source for exact body |
| delete_collection | voice_agent_backend/app/services/qdrant_service.py:101 | async | inferred from module/name; inspect source for exact body |
| collection_exists | voice_agent_backend/app/services/qdrant_service.py:110 | async | inferred from module/name; inspect source for exact body |
| list_documents | voice_agent_backend/app/services/qdrant_service.py:122 | async | inferred from module/name; inspect source for exact body |
| delete_document_vectors | voice_agent_backend/app/services/qdrant_service.py:166 | async | inferred from module/name; inspect source for exact body |
| upsert_points | voice_agent_backend/app/services/qdrant_service.py:183 | async | inferred from module/name; inspect source for exact body |
| search_vectors | voice_agent_backend/app/services/qdrant_service.py:201 | async | inferred from module/name; inspect source for exact body |
| health_check | voice_agent_backend/app/services/qdrant_service.py:234 | async | inferred from module/name; inspect source for exact body |
| __init__ | voice_agent_backend/app/services/speech_service.py:35 | sync | inferred from module/name; inspect source for exact body |
| precompute_backchannels | voice_agent_backend/app/services/speech_service.py:43 | async | inferred from module/name; inspect source for exact body |
| get_backchannel | voice_agent_backend/app/services/speech_service.py:68 | sync | inferred from module/name; inspect source for exact body |
| _normalize_tts_text | voice_agent_backend/app/services/speech_service.py:79 | sync | inferred from module/name; inspect source for exact body |
| replace_currency | voice_agent_backend/app/services/speech_service.py:93 | sync | inferred from module/name; inspect source for exact body |
| replace_ordinals | voice_agent_backend/app/services/speech_service.py:104 | sync | inferred from module/name; inspect source for exact body |
| replace_numbers | voice_agent_backend/app/services/speech_service.py:122 | sync | inferred from module/name; inspect source for exact body |
| _get_kokoro_pipeline | voice_agent_backend/app/services/speech_service.py:155 | sync | inferred from module/name; inspect source for exact body |
| get_available_voices | voice_agent_backend/app/services/speech_service.py:239 | sync | inferred from module/name; inspect source for exact body |
| _synthesize_native_chunks | voice_agent_backend/app/services/speech_service.py:257 | sync | inferred from module/name; inspect source for exact body |
| synthesize_stream | voice_agent_backend/app/services/speech_service.py:297 | async | inferred from module/name; inspect source for exact body |
| _fill_queue | voice_agent_backend/app/services/speech_service.py:316 | sync | inferred from module/name; inspect source for exact body |
| _synthesize_docker | voice_agent_backend/app/services/speech_service.py:371 | async | inferred from module/name; inspect source for exact body |
| transcribe | voice_agent_backend/app/services/speech_service.py:387 | async | inferred from module/name; inspect source for exact body |
| _transcribe_groq | voice_agent_backend/app/services/speech_service.py:405 | async | inferred from module/name; inspect source for exact body |
| _transcribe_local | voice_agent_backend/app/services/speech_service.py:431 | async | inferred from module/name; inspect source for exact body |
| configure_onnxruntime_gpu_environment | voice_agent_backend/scratch/benchmark_tts.py:23 | sync | inferred from module/name; inspect source for exact body |
| benchmark_hardware | voice_agent_backend/scratch/benchmark_tts.py:35 | async | inferred from module/name; inspect source for exact body |
| main | voice_agent_backend/scratch/benchmark_tts.py:102 | async | inferred from module/name; inspect source for exact body |
| rrf_score | voice_agent_backend/scratch/sim_scoring.py:3 | sync | inferred from module/name; inspect source for exact body |
| chunk_text_simple | voice_agent_backend/scratch/test_chunking.py:14 | sync | inferred from module/name; inspect source for exact body |
| recursive_split_inner | voice_agent_backend/scratch/test_chunking.py:16 | sync | inferred from module/name; inspect source for exact body |
| check_cuda_optimization | voice_agent_backend/scratch/test_hardware.py:7 | sync | inferred from module/name; inspect source for exact body |
| normalize | voice_agent_backend/scratch/test_normalization.py:4 | sync | inferred from module/name; inspect source for exact body |
| test_streaming_answer | voice_agent_backend/scratch/test_pipeline.py:13 | async | inferred from module/name; inspect source for exact body |
| main | voice_agent_backend/scratch/test_rag.py:12 | async | inferred from module/name; inspect source for exact body |
| test_normalization | voice_agent_backend/scratch/test_speech_norm.py:9 | sync | inferred from module/name; inspect source for exact body |
| run_health_checks | voice_agent_backend/scripts/check_backend_health.py:11 | async | inferred from module/name; inspect source for exact body |
| test | voice_agent_backend/scripts/test_imports.py:16 | sync | inferred from module/name; inspect source for exact body |
| test_search | voice_agent_backend/scripts/test_search_node.py:9 | async | inferred from module/name; inspect source for exact body |
| verify_kokoro | voice_agent_backend/scripts/verify_kokoro.py:8 | sync | inferred from module/name; inspect source for exact body |
| main | voice_agent_backend/test_graph.py:10 | async | inferred from module/name; inspect source for exact body |
| _make_handler | voice_agent_backend/tests/test_frontend.py:30 | sync | inferred from module/name; inspect source for exact body |
| _start_server | voice_agent_backend/tests/test_frontend.py:38 | sync | inferred from module/name; inspect source for exact body |
| setup_module | voice_agent_backend/tests/test_frontend.py:52 | sync | inferred from module/name; inspect source for exact body |
| teardown_module | voice_agent_backend/tests/test_frontend.py:57 | sync | inferred from module/name; inspect source for exact body |
| _intercept_health | voice_agent_backend/tests/test_frontend.py:63 | sync | inferred from module/name; inspect source for exact body |
| _intercept_collections | voice_agent_backend/tests/test_frontend.py:76 | sync | inferred from module/name; inspect source for exact body |
| _intercept_models | voice_agent_backend/tests/test_frontend.py:85 | sync | inferred from module/name; inspect source for exact body |
| _intercept_chat | voice_agent_backend/tests/test_frontend.py:100 | sync | inferred from module/name; inspect source for exact body |
| _intercept_401 | voice_agent_backend/tests/test_frontend.py:114 | sync | inferred from module/name; inspect source for exact body |
| _mock_all_api | voice_agent_backend/tests/test_frontend.py:123 | sync | inferred from module/name; inspect source for exact body |
| test_page_title | voice_agent_backend/tests/test_frontend.py:137 | sync | inferred from module/name; inspect source for exact body |
| test_orb_canvas_present | voice_agent_backend/tests/test_frontend.py:146 | sync | inferred from module/name; inspect source for exact body |
| test_status_bar_visible | voice_agent_backend/tests/test_frontend.py:156 | sync | inferred from module/name; inspect source for exact body |
| test_text_input_present | voice_agent_backend/tests/test_frontend.py:165 | sync | inferred from module/name; inspect source for exact body |
| test_control_bar_buttons_present | voice_agent_backend/tests/test_frontend.py:174 | sync | inferred from module/name; inspect source for exact body |
| test_message_list_on_load | voice_agent_backend/tests/test_frontend.py:185 | sync | inferred from module/name; inspect source for exact body |
| test_settings_panel_hidden_on_load | voice_agent_backend/tests/test_frontend.py:206 | sync | inferred from module/name; inspect source for exact body |
| test_settings_panel_opens_on_button_click | voice_agent_backend/tests/test_frontend.py:217 | sync | inferred from module/name; inspect source for exact body |
| test_settings_panel_closes_on_close_button | voice_agent_backend/tests/test_frontend.py:231 | sync | inferred from module/name; inspect source for exact body |
| test_documents_panel_opens | voice_agent_backend/tests/test_frontend.py:249 | sync | inferred from module/name; inspect source for exact body |
| test_documents_panel_has_drop_zone | voice_agent_backend/tests/test_frontend.py:261 | sync | inferred from module/name; inspect source for exact body |
| test_documents_panel_closes | voice_agent_backend/tests/test_frontend.py:272 | sync | inferred from module/name; inspect source for exact body |
| test_text_input_accepts_typing | voice_agent_backend/tests/test_frontend.py:290 | sync | inferred from module/name; inspect source for exact body |
| test_text_input_clears_after_send | voice_agent_backend/tests/test_frontend.py:301 | sync | inferred from module/name; inspect source for exact body |
| test_enter_key_triggers_send | voice_agent_backend/tests/test_frontend.py:320 | sync | inferred from module/name; inspect source for exact body |
| test_status_items_present | voice_agent_backend/tests/test_frontend.py:342 | sync | inferred from module/name; inspect source for exact body |
| test_collection_select_present | voice_agent_backend/tests/test_frontend.py:352 | sync | inferred from module/name; inspect source for exact body |
| test_ctrl_comma_opens_settings | voice_agent_backend/tests/test_frontend.py:365 | sync | inferred from module/name; inspect source for exact body |
| test_escape_closes_open_panel | voice_agent_backend/tests/test_frontend.py:377 | sync | inferred from module/name; inspect source for exact body |
| test_buttons_have_aria_labels | voice_agent_backend/tests/test_frontend.py:395 | sync | inferred from module/name; inspect source for exact body |
| test_no_js_errors_on_load | voice_agent_backend/tests/test_frontend.py:406 | sync | inferred from module/name; inspect source for exact body |
| test_html_lang_attribute | voice_agent_backend/tests/test_frontend.py:419 | sync | inferred from module/name; inspect source for exact body |

## Data Model Index
| Model / Schema | Evidence | Queried By |
| --- | --- | --- |
| docs/intelligence/_generate_docs.py:163 | if re.search(r"class .*BaseModel\|class .*Base\)\|mapped_column\(\|ForeignKey\(\|Base\.metadata\|create_all", line): | see query audit |
| docs/intelligence/_generate_docs.py:169 | if re.search(r"select\(\|db\.execute\|commit\(\|create_all\|_qdrant_\|search_vectors\|upsert_points\|scroll\|points/delete", line): | see query audit |
| voice_agent_backend/app/api/routes/auth.py:12 | class UserRegister(BaseModel): | see query audit |
| voice_agent_backend/app/api/routes/auth.py:16 | class Token(BaseModel): | see query audit |
| voice_agent_backend/app/api/routes/tts.py:11 | class TTSRequest(BaseModel): | see query audit |
| voice_agent_backend/app/core/database.py:14 | class Base(DeclarativeBase): | see query audit |
| voice_agent_backend/app/core/database.py:23 | await conn.run_sync(Base.metadata.create_all) | see query audit |
| voice_agent_backend/app/models/schemas.py:5 | class ChatRequest(BaseModel): | see query audit |
| voice_agent_backend/app/models/schemas.py:16 | class STTResponse(BaseModel): | see query audit |
| voice_agent_backend/app/models/schemas.py:21 | class CollectionCreateRequest(BaseModel): | see query audit |
| voice_agent_backend/app/models/schemas.py:26 | class DocumentInfo(BaseModel): | see query audit |
| voice_agent_backend/app/models/schemas.py:32 | class IngestResponse(BaseModel): | see query audit |
| voice_agent_backend/app/models/schemas.py:41 | class ChatStreamRequest(BaseModel): | see query audit |
| voice_agent_backend/app/models/schemas.py:61 | class InterruptRequest(BaseModel): | see query audit |
| voice_agent_backend/app/models/user.py:6 | class User(Base): | see query audit |
| voice_agent_backend/app/models/user.py:9 | id: Mapped[int] = mapped_column(primary_key=True, index=True) | see query audit |
| voice_agent_backend/app/models/user.py:10 | email: Mapped[str] = mapped_column(String(255), unique=True, index=True) | see query audit |
| voice_agent_backend/app/models/user.py:11 | password_hash: Mapped[str] = mapped_column(String(255)) | see query audit |
| voice_agent_backend/app/models/user.py:12 | is_active: Mapped[bool] = mapped_column(default=True) | see query audit |
| voice_agent_backend/app/models/user.py:13 | created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow) | see query audit |
| voice_agent_backend/app/models/user.py:15 | class UserSession(Base): | see query audit |
| voice_agent_backend/app/models/user.py:18 | id: Mapped[str] = mapped_column(String(128), primary_key=True, index=True) | see query audit |
| voice_agent_backend/app/models/user.py:19 | user_id: Mapped[int] = mapped_column(ForeignKey("users.id")) | see query audit |
| voice_agent_backend/app/models/user.py:20 | expires_at: Mapped[datetime] = mapped_column() | see query audit |
| voice_agent_backend/app/models/user.py:21 | created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow) | see query audit |

## Config/Env Index
| Var | Defined At | Where Used | Required/Optional | Default |
| --- | --- | --- | --- | --- |
| OLLAMA_BASE | voice_agent_backend/app/core/config.py:58 | docs/intelligence/_generate_docs.py:388, voice_agent_backend/app/services/ollama_service.py:14, voice_agent_backend/app/services/ollama_service.py:60, voice_agent_backend/app/services/ollama_service.py:110, voice_agent_backend/app/services/ollama_service.py:123, voice_agent_backend/plan.md:451, voice_agent_backend/scripts/check_backend_health.py:16 | defaulted/feature-specific | "http://localhost:11434" |
| QDRANT_BASE | voice_agent_backend/app/core/config.py:59 | docs/intelligence/_generate_docs.py:389, voice_agent_backend/app/services/qdrant_service.py:14, voice_agent_backend/app/services/qdrant_service.py:29, voice_agent_backend/app/services/qdrant_service.py:44, voice_agent_backend/app/services/qdrant_service.py:59, voice_agent_backend/app/services/qdrant_service.py:237, voice_agent_backend/plan.md:543, voice_agent_backend/scripts/check_backend_health.py:20 | defaulted/feature-specific | "http://localhost:6333" |
| GROQ_BASE | voice_agent_backend/app/core/config.py:60 | docs/intelligence/_generate_docs.py:387, docs/intelligence/_generate_docs.py:395, voice_agent_backend/app/services/groq_service.py:25, voice_agent_backend/app/services/groq_service.py:87, voice_agent_backend/app/services/groq_service.py:124, voice_agent_backend/app/services/groq_service.py:139, voice_agent_backend/app/services/speech_service.py:408, voice_agent_backend/scripts/check_backend_health.py:24 | defaulted/feature-specific | "https://api.groq.com/openai/v1" |
| GROQ_API_KEY | voice_agent_backend/app/core/config.py:61 | docs/intelligence/_generate_docs.py:395, voice_agent_backend/app/services/groq_service.py:27, voice_agent_backend/app/services/groq_service.py:89, voice_agent_backend/app/services/groq_service.py:125, voice_agent_backend/app/services/groq_service.py:140, voice_agent_backend/app/services/speech_service.py:407, voice_agent_backend/plan.md:683, voice_agent_backend/plan.md:689 | required for provider/security | "" |
| CHAT_MODEL | voice_agent_backend/app/core/config.py:64 | voice_agent_backend/app/api/routes/chat.py:238, voice_agent_backend/app/api/routes/chat.py:395, voice_agent_backend/app/core/nodes/generate_response.py:140, voice_agent_backend/app/core/nodes/handle_early_exit.py:89, voice_agent_backend/plan.md:680 | defaulted/feature-specific | "llama-3.1-8b-instant" |
| EMBED_MODEL | voice_agent_backend/app/core/config.py:65 | voice_agent_backend/app/api/routes/chat.py:397, voice_agent_backend/app/api/routes/collections.py:31, voice_agent_backend/app/api/routes/ingest.py:347, voice_agent_backend/app/api/routes/ingest.py:352, voice_agent_backend/app/core/langchain_rag.py:314, voice_agent_backend/plan.md:450, voice_agent_backend/plan.md:479 | defaulted/feature-specific | "mxbai-embed-large:latest" |
| TRANSLATION_MODEL | voice_agent_backend/app/core/config.py:66 | voice_agent_backend/app/core/translation.py:19, voice_agent_backend/app/core/translation.py:45, voice_agent_backend/plan.md:686 | defaulted/feature-specific | "llama-3.1-8b-instant" |
| CHAT_PROVIDER | voice_agent_backend/app/core/config.py:68 | voice_agent_backend/app/api/routes/chat.py:239, voice_agent_backend/app/api/routes/chat.py:396, voice_agent_backend/app/core/nodes/generate_response.py:141, voice_agent_backend/app/core/nodes/handle_early_exit.py:90 | defaulted/feature-specific | "groq"  # "groq" or "ollama" |
| TRANSLATION_PROVIDER | voice_agent_backend/app/core/config.py:69 | voice_agent_backend/app/core/translation.py:20, voice_agent_backend/app/core/translation.py:46 | defaulted/feature-specific | "groq"  # "groq" or "ollama" |
| DEFAULT_COLLECTION | voice_agent_backend/app/core/config.py:72 | no direct settings usage found | defaulted/feature-specific | "agent_knowledge" |
| RETRIEVAL_TOP_K | voice_agent_backend/app/core/config.py:73 | voice_agent_backend/app/core/langchain_rag.py:308 | defaulted/feature-specific | 12  # Increased from 8 for better recall on rare entities |
| SUMMARY_TOP_K | voice_agent_backend/app/core/config.py:74 | voice_agent_backend/app/core/langchain_rag.py:308, voice_agent_backend/app/core/langchain_rag.py:357 | defaulted/feature-specific | 16 |
| RERANK_TOP_N | voice_agent_backend/app/core/config.py:75 | voice_agent_backend/app/core/langchain_rag.py:354 | defaulted/feature-specific | 6 |
| SCORE_THRESHOLD | voice_agent_backend/app/core/config.py:76 | voice_agent_backend/app/core/langchain_rag.py:309 | defaulted/feature-specific | 0.25  # Lowered slightly to capture more candidates for consensus |
| RETRIEVAL_CONFIDENCE_FLOOR | voice_agent_backend/app/core/config.py:77 | voice_agent_backend/app/core/langchain_rag.py:205 | defaulted/feature-specific | 0.40  # Unified scale for RRF + Vector |
| SUMMARY_CONFIDENCE_FLOOR | voice_agent_backend/app/core/config.py:78 | voice_agent_backend/app/core/langchain_rag.py:205 | defaulted/feature-specific | 0.35 |
| CHUNK_SIZE | voice_agent_backend/app/core/config.py:81 | voice_agent_backend/app/api/routes/ingest.py:21, voice_agent_backend/scratch/test_chunking.py:29, voice_agent_backend/scratch/test_chunking.py:35 | defaulted/feature-specific | 1200 |
| CHUNK_OVERLAP | voice_agent_backend/app/core/config.py:82 | voice_agent_backend/app/api/routes/ingest.py:22, voice_agent_backend/scratch/test_chunking.py:45 | defaulted/feature-specific | 200 |
| MEMORY_PAIRS | voice_agent_backend/app/core/config.py:85 | voice_agent_backend/app/api/routes/chat.py:234 | defaulted/feature-specific | 10 |
| KOKORO_MODE | voice_agent_backend/app/core/config.py:89 | no direct settings usage found | defaulted/feature-specific | "native" |
| KOKORO_DOCKER_URL | voice_agent_backend/app/core/config.py:91 | no direct settings usage found | defaulted/feature-specific | "http://127.0.0.1:8880" |
| KOKORO_MODEL_PATH | voice_agent_backend/app/core/config.py:93 | voice_agent_backend/app/api/routes/models.py:22 | defaulted/feature-specific | "../kokoro-v1.0.onnx" |
| KOKORO_VOICES_PATH | voice_agent_backend/app/core/config.py:95 | no direct settings usage found | defaulted/feature-specific | "../voices-v1.0.bin" |
| KOKORO_LANG_CODE | voice_agent_backend/app/core/config.py:97 | no direct settings usage found | defaulted/feature-specific | "a" |
| TTS_HARDWARE | voice_agent_backend/app/core/config.py:99 | no direct settings usage found | defaulted/feature-specific | "gpu" |
| TTS_SAMPLE_RATE | voice_agent_backend/app/core/config.py:101 | no direct settings usage found | defaulted/feature-specific | 24000 |
| CONTEXT_WINDOW_TURNS | voice_agent_backend/app/core/config.py:103 | no direct settings usage found | defaulted/feature-specific | 3 |
| CORRELATOR_MODEL | voice_agent_backend/app/core/config.py:105 | no direct settings usage found | defaulted/feature-specific | "meta-llama/llama-4-scout-17b-16e-instruct" |
| CORRELATOR_PROVIDER | voice_agent_backend/app/core/config.py:107 | no direct settings usage found | defaulted/feature-specific | "groq" |
| BACKCHANNEL_PHRASES | voice_agent_backend/app/core/config.py:110 | no direct settings usage found | defaulted/feature-specific | ["mm-hmm", "yeah", "I see", "got it", "right"] |
| BACKCHANNEL_COOLDOWN_SECONDS | voice_agent_backend/app/core/config.py:111 | voice_agent_backend/app/api/routes/chat.py:337, voice_agent_backend/app/api/routes/chat.py:424 | defaulted/feature-specific | 6.0 |
| PREDICTIVE_RAG_TIMEOUT_MS | voice_agent_backend/app/core/config.py:112 | no direct settings usage found | defaulted/feature-specific | 500 |
| ENABLE_SEARCH | voice_agent_backend/app/core/config.py:115 | no direct settings usage found | defaulted/feature-specific | True |
| SEARCH_PROVIDER | voice_agent_backend/app/core/config.py:116 | no direct settings usage found | defaulted/feature-specific | "duckduckgo" # "duckduckgo" or "tavily" |
| TAVILY_API_KEY | voice_agent_backend/app/core/config.py:117 | no direct settings usage found | defaulted/feature-specific | "" |
| CORS_ORIGINS | voice_agent_backend/app/core/config.py:120 | no direct settings usage found | defaulted/feature-specific | ["http://localhost:8000", "http://127.0.0.1:8000"] |
| ALLOWED_HOSTS | voice_agent_backend/app/core/config.py:121 | no direct settings usage found | defaulted/feature-specific | ["localhost", "127.0.0.1"] |
| SECRET_KEY | voice_agent_backend/app/core/config.py:124 | voice_agent_backend/app/core/auth.py:35, voice_agent_backend/app/core/auth.py:57 | required for provider/security | [REDACTED fallback secret default] |
| ALGORITHM | voice_agent_backend/app/core/config.py:125 | voice_agent_backend/app/core/auth.py:35, voice_agent_backend/app/core/auth.py:57 | defaulted/feature-specific | "HS256" |
| ACCESS_TOKEN_EXPIRE_MINUTES | voice_agent_backend/app/core/config.py:126 | voice_agent_backend/app/core/auth.py:31 | defaulted/feature-specific | 60 |
| MAX_FILE_SIZE | voice_agent_backend/app/core/config.py:127 | voice_agent_backend/app/api/routes/ingest.py:410, voice_agent_backend/app/api/routes/ingest.py:413 | defaulted/feature-specific | 50 * 1024 * 1024  # 50 MB |
| ENABLE_RATE_LIMIT | voice_agent_backend/app/core/config.py:128 | voice_agent_backend/app/core/limiter.py:7 | defaulted/feature-specific | True |
| HOST | voice_agent_backend/app/core/config.py:148 | no direct settings usage found | defaulted/feature-specific | "0.0.0.0" |
| PORT | voice_agent_backend/app/core/config.py:149 | no direct settings usage found | defaulted/feature-specific | 8000 |
| IO_THREAD_POOL_SIZE | voice_agent_backend/app/core/config.py:153 | voice_agent_backend/app/main.py:51, voice_agent_backend/app/main.py:52 | defaulted/feature-specific | 12 |
| GPU_BATCH_SIZE | voice_agent_backend/app/core/config.py:154 | voice_agent_backend/app/api/routes/ingest.py:356 | defaulted/feature-specific | 4 |
| ONNX_INTRA_OP_THREADS | voice_agent_backend/app/core/config.py:155 | voice_agent_backend/app/services/speech_service.py:198 | defaulted/feature-specific | 4 |
| ONNX_INTER_OP_THREADS | voice_agent_backend/app/core/config.py:156 | voice_agent_backend/app/services/speech_service.py:199 | defaulted/feature-specific | 2 |
| MODELS_TO_CUDA | voice_agent_backend/app/core/config.py:157 | no direct settings usage found | defaulted/feature-specific | ["kokoro", "embed"] |
| STT_LOCAL_DEVICE | voice_agent_backend/app/core/config.py:158 | no direct settings usage found | defaulted/feature-specific | "cpu"  # Keep STT on CPU to save 4GB VRAM for RAG/TTS |

## External Service Index
| Service | Credential Source | Failure Behavior | Retry |
| --- | --- | --- | --- |
| Groq | GROQ_API_KEY | route/service exception or health offline | no central retry found |
| Ollama | none/local | empty models/offline/errors | no central retry found |
| Qdrant | none observed | empty result/dict or route error | no central retry found |
| Kokoro native/Docker | local files or local sidecar | TTS degradation/warning | no central retry found |
| DuckDuckGo/Tavily | TAVILY_API_KEY if Tavily selected | search degradation/error | not centrally determined |

## Known Bug Index
| Bug | File:Line | Severity | Reproduction | Fix Approach |
| --- | --- | --- | --- | --- |
| R-001 | voice_agent_backend/app/main.py:102 | HIGH | Auth router is imported but not mounted; register/login endpoints are not live through the app entrypoint. | Include auth.router or remove disconnected auth UI/docs. |
| R-002 | voice_agent_backend/app/api/routes/collections.py:39 | HIGH | Unauthenticated write/delete routes can mutate Qdrant collections and documents. | Protect write/delete routes or explicitly document guest-only local trust boundary. |
| R-003 | voice_agent_backend/app/core/config.py:124 | HIGH | A fallback JWT secret lets the app start insecurely if production env omits SECRET_KEY. | Fail startup when SECRET_KEY is default outside local dev. |
| R-004 | voice_agent_backend/app/api/routes/ingest.py:390 | HIGH | Ingest ignores Qdrant upsert response; failed vector writes can still return success. | Check and propagate Qdrant write failures. |
| R-005 | voice_agent_backend/app/api/routes/chat.py:456 | MEDIUM | Graph task is created without await/cancel plumbing; exceptions can leave SSE waiting. | Capture task exceptions, cancel on disconnect, and always signal done. |
| R-006 | voice_agent_backend/frontend/script.js:1195 | MEDIUM | Markdown is rendered into innerHTML without sanitizer. | Sanitize LLM Markdown output before DOM insertion. |
| R-007 | voice_agent_backend/app/core/memory.py:13 | MEDIUM | Session/cache/checkpoint state is process-local and not multi-worker safe. | Use durable storage or document single-worker limitation. |
| R-008 | voice_agent_backend/start_server.bat:8 | MEDIUM | Scripts mention .env.example, but no template exists in the live file tree. | Create a sanitized env template. |
| R-009 | voice_agent_backend/app/api/routes/ingest.py:422 | MEDIUM | safe_filename is computed but raw filename remains in payload/source paths. | Use sanitized filename consistently. |
| R-010 | voice_agent_backend/tests/test_frontend.py:4 | MEDIUM | Tests mock frontend APIs and do not exercise backend routes/providers. | Add backend route and service tests with mocked providers. |

## Test Index
| Test File | What It Tests | What It Does Not Test | Fixture Accuracy |
| --- | --- | --- | --- |
| voice_agent_backend/scratch/test_chunking.py | frontend/static or manual/scratch behavior | backend provider/routing failure paths | mocked/manual; can drift |
| voice_agent_backend/scratch/test_hardware.py | frontend/static or manual/scratch behavior | backend provider/routing failure paths | mocked/manual; can drift |
| voice_agent_backend/scratch/test_normalization.py | frontend/static or manual/scratch behavior | backend provider/routing failure paths | mocked/manual; can drift |
| voice_agent_backend/scratch/test_pipeline.py | frontend/static or manual/scratch behavior | backend provider/routing failure paths | mocked/manual; can drift |
| voice_agent_backend/scratch/test_rag.py | frontend/static or manual/scratch behavior | backend provider/routing failure paths | mocked/manual; can drift |
| voice_agent_backend/scratch/test_speech_norm.py | frontend/static or manual/scratch behavior | backend provider/routing failure paths | mocked/manual; can drift |
| voice_agent_backend/scripts/test_imports.py | frontend/static or manual/scratch behavior | backend provider/routing failure paths | mocked/manual; can drift |
| voice_agent_backend/scripts/test_search_node.py | frontend/static or manual/scratch behavior | backend provider/routing failure paths | mocked/manual; can drift |
| voice_agent_backend/test_graph.py | frontend/static or manual/scratch behavior | backend provider/routing failure paths | mocked/manual; can drift |
| voice_agent_backend/tests/__init__.py | frontend/static or manual/scratch behavior | backend provider/routing failure paths | mocked/manual; can drift |
| voice_agent_backend/tests/test_frontend.py | frontend/static or manual/scratch behavior | backend provider/routing failure paths | mocked/manual; can drift |
