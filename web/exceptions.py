#
# ===========================================================================
#
#                            PUBLIC DOMAIN NOTICE
#               National Center for Biotechnology Information
#
#  This software/database is a "United States Government Work" under the
#  terms of the United States Copyright Act.  It was written as part of
#  the author's official duties as a United States Government employee and
#  thus cannot be copyrighted.  This software/database is freely available
#  to the public for use. The National Library of Medicine and the U.S.
#  Government have not placed any restriction on its use or reproduction.
#
#  Although all reasonable efforts have been taken to ensure the accuracy
#  and reliability of the software and data, the NLM and the U.S.
#  Government do not and cannot warrant the performance or results that
#  may be obtained by using this software or data. The NLM and the U.S.
#  Government disclaim all warranties, express or implied, including
#  warranties of performance, merchantability or fitness for any particular
#  purpose.
#
#  Please cite the author in any work or product based on this material.
#
# ===========================================================================
#
# Code author:  Aleksandar Stojmirovic
#
from cgi import escape

class WebException(Exception):
    def __str__(self):
        return 'Unexpected server error.'

class SaddleSumError(Exception):
    def __init__(self, err_msg):
        WebException.__init__(self)
        self.err_msg = err_msg

    def __str__(self):
        return self.err_msg


class ValidationError(WebException):
    def __init__(self, field, value):
        WebException.__init__(self)
        self.field = field
        self.value = value

    def __str__(self):
        return "'%s' is not a valid value for the field '%s'." % (self.value, self.field)


class OutOfRangeError(WebException):
    def __init__(self, field, value):
        WebException.__init__(self)
        self.field = field
        self.value = value

    def __str__(self):
        return "'%s': the value %s is out of the permitted range." % (self.field, self.value)


class InsufficientArgsError(WebException):
    def __init__(self, field):
        WebException.__init__(self)
        self.field = field

    def __str__(self):
        return "Insufficient arguments provided for the field '%s'." % self.field

class InsufficientSources(WebException):
    def __init__(self):
        WebException.__init__(self)

    def __str__(self):
        return "At least one source must be provided."

class InsufficientSinks(WebException):
    def __init__(self):
        WebException.__init__(self)

    def __str__(self):
        return "At least one sink must be provided."

class SingleProteinError(WebException):
    def __init__(self, field):
        WebException.__init__(self)
        self.field = field

    def __str__(self):
        return '%s may contain only one protein' % self.field

class PathwayError(WebException):
    def __init__(self, pathway):
        WebException.__init__(self)
        self.pathway = pathway

    def __str__(self):
        return 'Context #%d must have either both or none of sources and sinks specified.' % self.pathway


class MissingStoredResults(WebException):

    def __str__(self):
        return 'Stored results missing! Please rerun your query.'

class IdentifierNotFoundError(WebException):
    def __init__(self, field, value):
        WebException.__init__(self)
        self.field = field
        self.value = value

    def __str__(self):
        return "The identifier '%s' from the field '%s' does not belong to the specified network." % (self.value, self.field)

class BadIdentifier(WebException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class TooManyBoundaries(WebException):
    def __init__(self, field, max_val):
        WebException.__init__(self)
        self.field = field
        self.max_val = max_val

    def __str__(self):
        return "Too many %s specified (maximum %d)." % (self.field, self.max_val)

class TooLargeFile(WebException):
    def __init__(self):
        WebException.__init__(self)

    def __str__(self):
        return "Uploaded file is too large."

class ModelError(WebException):
    def __init__(self, value):
        WebException.__init__(self)
        self.value = value

    def __str__(self):
        return "Model Error: %s." % self.value

class WeightLineError(WebException):
    def __init__(self, line):
        WebException.__init__(self)
        self.line = line

    def __str__(self):
        return "Weights error: line %d is not in proper format." % self.line

class CutoffError(WebException):

    def __str__(self):
        return "A cutoff must be specified when using Fisher's Exact Test."
