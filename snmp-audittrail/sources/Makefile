SRCS = snmpAuditPlugin.c

OBJS = $(SRCS:.c=.o)
LDLIBS = -lfmcommon -lnetsnmp -lnetsnmpagent -luuid
INCLUDES += -I./
CCFLAGS = -fPIC -g -O2 -Wall -Werror
LIBCGTSAGENT_SO := libsnmpAuditPlugin.so
build: lib

.c.o:
	$(CXX) $(CCFLAGS) $(INCLUDES) -c $< -o $@

lib: $(OBJS)
	$(CXX) $(OBJS) $(LDLIBS) -o $(LIBCGTSAGENT_SO).$(MAJOR).$(MINOR).$(PATCH) -shared
	ln -sf $(LIBCGTSAGENT_SO).$(MAJOR).$(MINOR).$(PATCH) $(LIBCGTSAGENT_SO).$(MAJOR)
	ln -sf $(LIBCGTSAGENT_SO).$(MAJOR).$(MINOR).$(PATCH) $(LIBCGTSAGENT_SO)

clean:
	@rm -f $(OBJ) *.o *.so.*

install_non_bb:
	install -m 755 -d $(DEST_DIR)$(LIB_DIR)
	install -m 755 $(LIBCGTSAGENT_SO).$(MAJOR).$(MINOR).$(PATCH) $(DEST_DIR)$(LIB_DIR)
	ln -s $(LIBCGTSAGENT_SO).$(MAJOR).$(MINOR).$(PATCH) $(DEST_DIR)$(LIB_DIR)/$(LIBCGTSAGENT_SO).$(MAJOR)
	ln -s $(LIBCGTSAGENT_SO).$(MAJOR).$(MINOR).$(PATCH) $(DEST_DIR)$(LIB_DIR)/$(LIBCGTSAGENT_SO)
