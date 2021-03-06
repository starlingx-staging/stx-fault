#
# Copyright (c) 2013-2014 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

# -*- encoding: utf-8 -*-
#
#
# Author:
#

import copy
import subprocess
import constants
import six


class ClientException(Exception):
    pass

# Fields explanation:
#
# alarm_id: a text string of the alarm identifier
# alarm_state: see ALARM_STATE
# entity_type_id: type of the object raising alarm.
# entity_instance_id: instance information of the object raising alarm.
# severity: see ALARM_SEVERITY
# reason_text: free-format string providing description and additional details
#              on the alarm. Optional.
# alarm_type: see ALARM_TYPE
# probable_cause: see ALARM_PROBABLE_CAUSE
# proposed_repair_action:free-format string providing additional details on how to
#                        clear the alarm. Optional.
# service_affecting: true/false, default to false
# suppression: true/false (allowed/not-allowed), default to false
# uuid: unique identifier of an active alarm instance, filled by FM system
# Timestamp: when the alarm has been raised/updated, filled by FM system
# See CGCS FM Guide for the alarm model specification
class Fault(object):

    def __init__(self, alarm_id, alarm_state, entity_type_id,
                 entity_instance_id, severity, reason_text,
                 alarm_type, probable_cause, proposed_repair_action,
                 service_affecting=False, suppression=False,
                 uuid=None, timestamp=None):
        self.alarm_id = alarm_id
        self.alarm_state = alarm_state
        self.entity_type_id = self._unicode(entity_type_id)
        self.entity_instance_id = self._unicode(entity_instance_id)
        self.severity = severity
        self.reason_text = self._unicode(reason_text)
        self.alarm_type = alarm_type
        self.probable_cause = probable_cause
        self.proposed_repair_action = self._unicode(proposed_repair_action)
        self.service_affecting = service_affecting
        self.suppression = suppression
        self.uuid = uuid
        self.timestamp = timestamp

    def as_dict(self):
        return copy.copy(self.__dict__)

    @staticmethod
    def _unicode(value):
        if isinstance(value, str):
            return six.text_type(value.decode('utf-8'))
        else:
            return value


class FaultAPIs(object):

    def set_fault(self, data):
        self._check_required_attributes(data)
        self._validate_attributes(data)
        buff = self._alarm_to_str(data)
        cmd = constants.FM_CLIENT_SET_FAULT + '"' + buff + '"'
        resp = self._run_cmd_and_get_resp(cmd)
        if (resp[0] == "Ok") and (len(resp) > 1):
            return resp[1]
        else:
            return None

    def clear_fault(self, alarm_id, entity_instance_id):
        sep = constants.FM_CLIENT_STR_SEP
        buff = (sep + self._check_val(alarm_id) + sep +
                self._check_val(entity_instance_id) + sep)
        cmd = constants.FM_CLIENT_CLEAR_FAULT + '"' + buff + '"'

        resp = self._run_cmd_and_get_resp(cmd)
        if resp[0] == "Ok":
            return True
        else:
            return False

    def get_fault(self, alarm_id, entity_instance_id):
        sep = constants.FM_CLIENT_STR_SEP
        buff = (sep + self._check_val(alarm_id) + sep +
                self._check_val(entity_instance_id) + sep)
        cmd = constants.FM_CLIENT_GET_FAULT + '"' + buff + '"'
        resp = self._run_cmd_and_get_resp(cmd)
        if (resp[0] == "Ok") and (len(resp) > 1):
            return self._str_to_alarm(resp[1])
        else:
            return None

    def clear_all(self, entity_instance_id):
        cmd = constants.FM_CLIENT_CLEAR_ALL + '"' + entity_instance_id + '"'
        resp = self._run_cmd_and_get_resp(cmd)
        if resp[0] == "Ok":
            return True
        else:
            return False

    def get_faults(self, entity_instance_id):
        cmd = constants.FM_CLIENT_GET_FAULTS + '"' + entity_instance_id + '"'
        resp = self._run_cmd_and_get_resp(cmd)
        data = []
        if resp[0] == "Ok":
            for i in range(1, len(resp)):
                alarm = self._str_to_alarm(resp[i])
                data.append(alarm)
            return data
        else:
            return None

    def get_faults_by_id(self, alarm_id):
        cmd = constants.FM_CLIENT_GET_FAULTS_BY_ID + '"' + alarm_id + '"'
        resp = self._run_cmd_and_get_resp(cmd)
        data = []
        if resp[0] == "Ok":
            for i in range(1, len(resp)):
                alarm = self._str_to_alarm(resp[i])
                data.append(alarm)
            return data
        else:
            return None

    @staticmethod
    def _check_val(data):
        if data is None:
            return " "
        else:
            return data

    def _alarm_to_str(self, data):
        sep = constants.FM_CLIENT_STR_SEP
        return (sep + self._check_val(data.uuid) + sep + data.alarm_id + sep +
                data.alarm_state + sep + data.entity_type_id + sep +
                data.entity_instance_id + sep + self._check_val(data.timestamp)
                + sep + data.severity + sep + self._check_val(data.reason_text)
                + sep + data.alarm_type + sep + data.probable_cause + sep +
                self._check_val(data.proposed_repair_action) + sep +
                str(data.service_affecting) + sep + str(data.suppression) + sep)

    @staticmethod
    def _str_to_alarm(alarm_str):
        l = alarm_str.split(constants.FM_CLIENT_STR_SEP)
        if len(l) < constants.MAX_ALARM_ATTRIBUTES:
            return None
        else:
            data = Fault(l[constants.FM_ALARM_ID_INDEX],
                         l[constants.FM_ALARM_STATE_INDEX],
                         l[constants.FM_ENT_TYPE_ID_INDEX],
                         l[constants.FM_ENT_INST_ID_INDEX],
                         l[constants.FM_SEVERITY_INDEX],
                         l[constants.FM_REASON_TEXT_INDEX],
                         l[constants.FM_ALARM_TYPE_INDEX],
                         l[constants.FM_CAUSE_INDEX],
                         l[constants.FM_REPAIR_ACTION_INDEX],
                         l[constants.FM_SERVICE_AFFECTING_INDEX],
                         l[constants.FM_SUPPRESSION_INDEX],
                         l[constants.FM_UUID_INDEX],
                         l[constants.FM_TIMESTAMP_INDEX])
            return data

    @staticmethod
    def _run_cmd_and_get_resp(cmd):
        resp = []
        cmd = cmd.encode('utf-8')
        pro = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
        output = pro.communicate()[0]
        lines = output.split('\n')
        for line in lines:
            if line != '':
                resp.append(line)
        if len(resp) == 0:
            resp.append("Unknown")

        return resp

    @staticmethod
    def _check_required_attributes(data):
        if data.alarm_id is None:
            raise ClientException("Alarm  id is is required.")
        if data.alarm_state is None:
            raise ClientException("Alarm state is required.")
        if data.severity is None:
            raise ClientException("Severity is required.")
        if data.alarm_type is None:
            raise ClientException("Alarm type is required.")
        if data.probable_cause is None:
            raise ClientException("Probable Cause is required.")
        if data.entity_type_id is None:
            raise ClientException("Entity type id is required.")
        if data.entity_instance_id is None:
            raise ClientException("Entity instance id is required.")

    @staticmethod
    def _validate_attributes(data):
        """ Validate the attributes
            only applies to Telco specific attributes"""
        if data.alarm_state not in constants.ALARM_STATE:
                raise ClientException("Invalid Fault State: %s" %
                                      data.alarm_state)
        if data.severity not in constants.ALARM_SEVERITY:
                raise ClientException("Invalid Fault Severity: %s" %
                                      data.severity)
        if  data.alarm_type not in constants.ALARM_TYPE:
                raise ClientException("Invalid Fault Type: %s" %
                                      data.alarm_type)
        if  data.probable_cause not in constants.ALARM_PROBABLE_CAUSE:
                raise ClientException("Invalid Fault Probable Cause: %s" %
                                      data.probable_cause)

    @staticmethod
    def alarm_allowed(alarm_severity, threshold):
        def severity_to_int(severity):
            if severity == 'none':
                return 5
            elif severity == constants.FM_ALARM_SEVERITY_CRITICAL:
                return 4
            elif severity == constants.FM_ALARM_SEVERITY_MAJOR:
                return 3
            elif severity == constants.FM_ALARM_SEVERITY_MINOR:
                return 2
            elif severity == constants.FM_ALARM_SEVERITY_WARNING:
                return 1

        given = severity_to_int(alarm_severity)
        threshold = severity_to_int(threshold)
        if given < threshold:
            return True
        return False


