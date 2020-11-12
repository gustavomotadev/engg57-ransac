# ------------------------------------------------------------------------------
# Top Level Simulation Script to source msim_setup.tcl
# ------------------------------------------------------------------------------
set QSYS_SIMDIR obj/default/runtime/sim
source msim_setup.tcl
# Copy generated memory initialization hex and dat file(s) to current directory
file copy -force D:/Projetos/Quartus/AcumuladorNios/software/TesteSoftware/mem_init/hdl_sim/SistemaEmbarcado_MemoriaDados.dat ./ 
file copy -force D:/Projetos/Quartus/AcumuladorNios/software/TesteSoftware/mem_init/hdl_sim/SistemaEmbarcado_MemoriaPrograma.dat ./ 
file copy -force D:/Projetos/Quartus/AcumuladorNios/software/TesteSoftware/mem_init/SistemaEmbarcado_MemoriaDados.hex ./ 
file copy -force D:/Projetos/Quartus/AcumuladorNios/software/TesteSoftware/mem_init/SistemaEmbarcado_MemoriaPrograma.hex ./ 
